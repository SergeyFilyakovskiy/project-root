import logging

from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("gateway")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"{request.method} {request.url.path} from {request.client.host}") # type: ignore
        response = await call_next(request)
        if response.status_code >= 400:
            logger.warning(f"[{response.status_code}] {request.method} {request.url.path}")
        return response
