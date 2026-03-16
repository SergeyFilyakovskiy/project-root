import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import (
    IntegrationCreate, IntegrationUpdate,
    IntegrationResponse, IntegrationListResponse,
    OAuthInitResponse, TokenStatusResponse,
)
from app.repositories.integration_repo import IntegrationRepo
from app.services.integration_service import IntegrationService
from app.services.token_service import TokenService
from app.core.dependencies import user_dependency, redis_dependency, postgres_dependency
from app.api.schemas import PlatformEnum
from app.core.config import settings
import httpx
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/integrations", tags=["integrations"])

OAUTH_URLS = {
    PlatformEnum.GOOGLE_ADS: "https://accounts.google.com/o/oauth2/auth",
    PlatformEnum.YANDEX_DIRECT: "https://oauth.yandex.ru/authorize",
    PlatformEnum.META_ADS: "https://www.facebook.com/v21.0/dialog/oauth",
}

OAUTH_SCOPES = {
    PlatformEnum.GOOGLE_ADS: "https://www.googleapis.com/auth/adwords",
    PlatformEnum.YANDEX_DIRECT: "direct:api",
    PlatformEnum.META_ADS: "ads_management,ads_read",
}


def get_service(session: postgres_dependency) -> IntegrationService:
    return IntegrationService(IntegrationRepo(session))


def get_token_service(session: postgres_dependency) -> TokenService:
    return TokenService(IntegrationRepo(session))


# --- CRUD ---

@router.post("/", response_model=IntegrationResponse, status_code=201)
async def create_integration(
    data: IntegrationCreate,
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
):
    return await service.create(user_id, data)


@router.get("/", response_model=IntegrationListResponse)
async def list_integrations(
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
):
    items = await service.get_all(user_id)
    return IntegrationListResponse(items=items, total=len(items))


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: uuid.UUID,
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
):
    try:
        return await service.get_by_id(integration_id, user_id)
    except ValueError:
        raise HTTPException(404, "Integration not found")


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: uuid.UUID,
    data: IntegrationUpdate,
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
):
    try:
        return await service.update(integration_id, user_id, data)
    except ValueError:
        raise HTTPException(404, "Integration not found")


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: uuid.UUID,
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
):
    try:
        await service.delete(integration_id, user_id)
    except ValueError:
        raise HTTPException(404, "Integration not found")


# --- OAuth ---

@router.get("/{integration_id}/oauth/init", response_model=OAuthInitResponse)
async def oauth_init(
    integration_id: uuid.UUID,
    user_id: user_dependency,
    redis_connection: redis_dependency,
    service: IntegrationService = Depends(get_service),
):
    integration = await service.get_by_id(integration_id, user_id)
    platform = PlatformEnum(integration.platform)

    state = f"{integration_id}:{int(time.time())}"
    await redis_connection.set(f"oauth_state:{state}", str(integration_id), ex=600)

    params = {
        "client_id": getattr(settings, f"{platform.value.split('_')[0]}_client_id"),
        "redirect_uri": getattr(settings, f"{platform.value.split('_')[0]}_redirect_uri"),
        "response_type": "code",
        "scope": OAUTH_SCOPES[platform],
        "state": state,
        **({"access_type": "offline", "prompt": "consent"} if platform == PlatformEnum.GOOGLE_ADS else {}),
    }

    base_url = OAUTH_URLS[platform]
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return OAuthInitResponse(auth_url=f"{base_url}?{query}")


@router.get("/oauth/callback")
async def oauth_callback(
    code: str,
    state: str,
    session: postgres_dependency,
    redis: redis_dependency,
):
    integration_id_raw = await redis.getdel(f"oauth_state:{state}")
    if not integration_id_raw:
        raise HTTPException(400, "Invalid or expired state")

    integration_id = uuid.UUID(integration_id_raw)
    repo = IntegrationRepo(session)
    integration = await repo.get_by_id(integration_id)
    if not integration:
        raise HTTPException(404, "Integration not found")

    token_data = await _exchange_code(code, PlatformEnum(integration.platform))
    await repo.save_tokens(
        integration_id=integration_id,
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_expires_at=token_data["expires_at"],
    )
    return {"status": "ok", "integration_id": str(integration_id)}


@router.get("/{integration_id}/token/status", response_model=TokenStatusResponse)
async def token_status(
    integration_id: uuid.UUID,
    user_id: user_dependency,
    service: IntegrationService = Depends(get_service),
    token_service: TokenService = Depends(get_token_service),
):
    integration = await service.get_by_id(integration_id, user_id)
    is_valid = (
        integration.access_token is not None
        and integration.token_expires_at is not None
        and integration.token_expires_at > datetime.now(timezone.utc)
    )
    return TokenStatusResponse(
        integration_id=integration_id,
        is_valid=is_valid,
        expires_at=integration.token_expires_at,
    )


async def _exchange_code(code: str, platform: PlatformEnum) -> dict:
    token_urls = {
        PlatformEnum.GOOGLE_ADS: "https://oauth2.googleapis.com/token",
        PlatformEnum.YANDEX_DIRECT: "https://oauth.yandex.ru/token",
        PlatformEnum.META_ADS: "https://graph.facebook.com/oauth/access_token",
    }
    platform_key = platform.value.split("_")[0]  # google / yandex / meta

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_urls[platform],
            data={
                "client_id": getattr(settings, f"{platform_key}_client_id"),
                "client_secret": getattr(settings, f"{platform_key}_client_secret").get_secret_value(),
                "redirect_uri": getattr(settings, f"{platform_key}_redirect_uri"),
                "code": code,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print("Google response:", response.status_code, response.text)
        response.raise_for_status()
        data = response.json()

    expires_in = data.get("expires_in", 3600)
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
    }
