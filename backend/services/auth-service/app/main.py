from fastapi import FastAPI

from app.api import auth

app = FastAPI(
    title="API регистрации и авторизации",
    version='0.0.1',
    openapi_prefix='/auth-service',
)

app.include_router(router=auth.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
