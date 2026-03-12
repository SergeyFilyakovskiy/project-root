from fastapi import FastAPI
from app.routes.proxy import router as proxy_router
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
#from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(title="API Gateway")

app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
#app.add_middleware(RateLimitMiddleware)

app.include_router(proxy_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
