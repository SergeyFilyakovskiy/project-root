from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    auth_service_url: str = "http://auth-service:8001"
    analytics_service_url: str = "http://analytics-service:8002"
    integration_service_url: str = "http://integration-service:8003"

    # публичные маршруты — не требуют токена
    public_paths: list[str] = [
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/docs",
        "/auth/openapi.json",
        "/auth/redoc",
    ]

    class Config:
        env_file = ".env"

settings = Settings()
