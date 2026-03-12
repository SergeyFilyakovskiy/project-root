# import time
# from collections import defaultdict
# from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
# from starlette.requests import Request
# from starlette.responses import Response, JSONResponse


# # ip → [timestamp, timestamp, ...]
# request_counts: dict[str, list[float]] = defaultdict(list)

# RATE_LIMIT = 100       # запросов
# WINDOW_SECONDS = 60    # за 60 секунд


# class RateLimitMiddleware(BaseHTTPMiddleware):
#     async def dispatch(
#         self,
#         request: Request,
#         call_next: RequestResponseEndpoint
#     ) -> Response:

#         ip = request.client.host
#         now = time.time()

#         # оставляем только запросы в пределах окна
#         request_counts[ip] = [
#             t for t in request_counts[ip]
#             if now - t < WINDOW_SECONDS
#         ]

#         if len(request_counts[ip]) >= RATE_LIMIT:
#             return JSONResponse(
#                 {"detail": "Too many requests. Try again later."},
#                 status_code=429,
#                 headers={"Retry-After": str(WINDOW_SECONDS)}
#             )

#         request_counts[ip].append(now)
#         return await call_next(request)
