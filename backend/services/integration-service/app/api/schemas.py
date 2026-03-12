import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class PlatformEnum(str):

    GOOGLE_ADS = "google_ads"
    YANDEX_DIRECT = "yandex_direct"
    META_ADS = "meta_ads"


# --- Запросы ---

class IntegrationCreate(BaseModel):

    platform: PlatformEnum
    name: str = Field(min_length=1, max_length=255)
    platform_config: dict[str, Any] = Field(default_factory=dict)


class IntegrationUpdate(BaseModel):

    name: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None
    platform_config: dict[str, Any] | None = None


# --- Ответы ---
class IntegrationResponse(BaseModel):

    id: uuid.UUID
    user_id: int
    platform: str
    name: str
    is_active: bool
    platform_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationListResponse(BaseModel):

    items: list[IntegrationResponse]
    total: int

# Получить ссылку для авторизации на платформе
class OAuthInitRequest(BaseModel):
    platform: PlatformEnum
    integration_id: uuid.UUID

class OAuthInitResponse(BaseModel):
    auth_url: str  # редиректим пользователя сюда

# Callback после того как пользователь разрешил доступ
class OAuthCallbackRequest(BaseModel):
    code: str
    state: str  # в state храним integration_id

# Статус токена
class TokenStatusResponse(BaseModel):
    integration_id: uuid.UUID
    is_valid: bool
    expires_at: datetime | None
