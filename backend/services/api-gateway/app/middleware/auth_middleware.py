import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import logging

logger = logging.getLogger("gateway.auth")

EXEMPT_HEADERS = {"host", "content-length", "transfer-encoding"}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # пропускаем публичные пути
        if any(request.url.path.startswith(p) for p in settings.public_paths):
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            logger.warning(f"No token from {request.client.host} : {request.url.path}") # type: ignore
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.auth_service_url}/auth/verify",
                    cookies={"access_token": token},
                )

            if resp.status_code == 401:
                logger.warning(f"Invalid token from {request.client.host}") # type: ignore
                return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)

            if resp.status_code != 200:
                logger.error(f"Auth service returned {resp.status_code}")
                return JSONResponse({"detail": "Auth service error"}, status_code=502)

            # прокидываем данные юзера downstream сервисам через заголовки
            user_data = resp.json()
            request.state.user = user_data

            # добавляем в заголовки чтобы сервисы знали кто делает запрос
            request.headers.__dict__["_list"].extend([
                (b"x-user-id", str(user_data["id"]).encode()),
                (b"x-user-role", str(user_data["role"]).encode()),
                (b"x-user-email", str(user_data["email"]).encode()),
            ])

        except httpx.TimeoutException:
            logger.error(f"Auth service timeout from {request.client.host}") # type: ignore
            return JSONResponse({"detail": "Auth service unavailable"}, status_code=503)

        except httpx.ConnectError:
            logger.error("Cannot connect to auth-service")
            return JSONResponse({"detail": "Auth service unavailable"}, status_code=503)

        return await call_next(request)
