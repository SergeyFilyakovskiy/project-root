from fastapi import APIRouter, Request
from fastapi.responses import Response
import httpx
from app.core.config import settings

router = APIRouter()

ROUTES = {
    "auth-service": settings.auth_service_url,
    "analytics-service": settings.analytics_service_url,
    "integration-service": settings.integration_service_url,
}
SKIP_HEADERS = {"content-encoding", "transfer-encoding", "content-length"}

@router.api_route("/{service}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def proxy(request: Request, service: str, path: str = ""):
    base_url = ROUTES.get(service)

    if base_url is None:
        return Response(content="Service not found", status_code=404)

    url = f"{base_url}/{service}/{path}" if path else f"{base_url}/{service}"

    async with httpx.AsyncClient() as client:
        upstream = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
            cookies=request.cookies,
            params=request.query_params,
        )

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
    )

    for name, value in upstream.headers.multi_items():
        if name.lower() not in SKIP_HEADERS:
            response.headers.append(name, value)

    return response