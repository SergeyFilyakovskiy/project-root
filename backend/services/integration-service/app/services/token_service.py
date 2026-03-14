import httpx
from datetime import datetime, timezone, timedelta
from uuid import UUID
from app.repositories.integration_repo import IntegrationRepo
from app.core.config import settings


class TokenService:
    def __init__(self, repo: IntegrationRepo):
        self.repo = repo

    async def get_valid_token(self, integration_id: UUID) -> str:
        integration = await self.repo.get_by_id(integration_id)

        if not integration:
            raise ValueError(f"Integration {integration_id} not found")

        if not integration.access_token:
            raise ValueError(f"Integration {integration_id} has no token, OAuth required")


        if self._is_expired(integration.token_expires_at):
            return await self._refresh_token(integration)

        return integration.access_token

    def _is_expired(self, expires_at: datetime | None) -> bool:
        if expires_at is None:
            return True
        now = datetime.now(timezone.utc)
        return expires_at - now < timedelta(minutes=5)

    async def _refresh_token(self, integration) -> str:
        handler = self._get_handler(integration.platform)
        token_data = await handler(integration.refresh_token, integration.platform_config)

        await self.repo.save_tokens(
            integration_id=integration.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", integration.refresh_token),
            token_expires_at=token_data["expires_at"],
        )

        return token_data["access_token"]

    def _get_handler(self, platform: str):
        handlers = {
            "google_ads": self._refresh_google,
            "yandex_direct": self._refresh_yandex,
            "meta_ads": self._refresh_meta,
        }
        handler = handlers.get(platform)
        if not handler:
            raise ValueError(f"Unknown platform: {platform}")
        return handler

    async def _refresh_google(self, refresh_token: str, config: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret.get_secret_value(),
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": None, 
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"]),
        }

    async def _refresh_yandex(self, refresh_token: str, config: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "client_id": settings.yandex_client_id,
                    "client_secret": settings.yandex_client_secret.get_secret_value(),
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"]),
        }

    async def _refresh_meta(self, refresh_token: str, config: dict) -> dict:

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/oauth/access_token",
                params={
                    "client_id": settings.meta_client_id,
                    "client_secret": settings.meta_client_secret.get_secret_value(),
                    "grant_type": "fb_exchange_token",
                    "fb_exchange_token": refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data["access_token"], 
            "expires_at": datetime.now(timezone.utc) + timedelta(days=60),
        }
