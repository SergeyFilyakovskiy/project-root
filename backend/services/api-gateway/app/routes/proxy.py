from fastapi import APIRouter, Request
from fastapi.responses import Response
import httpx
from app.core.config import settings

router = APIRouter()

ROUTES = {

    "/auth": settings.auth_service_url,
    "/analytics": settings.analytics_service_url,
    "/integration": settings.integration_service_url,
}

@router.api_route("/{service}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def proxy(request: Request, service: str, path: str):
    prefix = f"/{service}"
    base_url = ROUTES.get(prefix)

    if base_url is None:
        return Response(content="Service not found", status_code=404)

    url = f"{base_url}/{service}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
            cookies=request.cookies,
            params=request.query_params,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
