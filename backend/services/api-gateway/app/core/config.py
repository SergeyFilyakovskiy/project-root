from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    auth_service_url: str = "http://auth-service:8000"
    analytics_service_url: str = "http://analytics-service:8000"
    integration_service_url: str = "http://integration-service:8000"

    public_paths: list[str] = [
        "/auth-service/auth/register",
        "/auth-service/auth/login",
        "/auth-service/auth/refresh",
        "/auth-service/docs",
        "/auth-service/docs/auth",
        "/auth-service/openapi.json",
        "/auth-service/redoc",
    ]


settings = Settings()
