import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any
from enum import StrEnum


class PlatformEnum(StrEnum):
    """
    Перечисление поддерживаемых рекламных платформ.

    Attributes:
        GOOGLE_ADS: Google Ads — требует offline access_type для получения refresh_token.
        YANDEX_DIRECT: Яндекс.Директ — ротирует refresh_token при каждом обновлении.
        META_ADS: Meta Ads — использует long-lived токены вместо классического refresh_token.
    """
    GOOGLE_ADS = "google_ads"
    YANDEX_DIRECT = "yandex_direct"
    META_ADS = "meta_ads"


# --- Запросы ---

class IntegrationCreate(BaseModel):
    """
    Схема для создания новой интеграции с рекламной платформой.
    Токены не передаются при создании — они получаются через OAuth-флоу.

    Attributes:
        platform: Рекламная платформа из PlatformEnum.
        name: Произвольное название интеграции для отображения в интерфейсе.
        platform_config: Специфичные для платформы параметры.
            Google Ads: {"customer_id": "...", "manager_id": "..."}
            Яндекс.Директ: {"client_login": "...", "agency_client_id": "..."}
            Meta Ads: {"ad_account_id": "...", "business_id": "..."}
    """
    platform: PlatformEnum
    name: str = Field(min_length=1, max_length=255)
    platform_config: dict[str, Any] = Field(default_factory=dict)


class IntegrationUpdate(BaseModel):
    """
    Схема для частичного обновления интеграции.
    Все поля опциональны — передаются только изменяемые.
    Платформа и токены через этот эндпоинт не меняются.

    Attributes:
        name: Новое название интеграции.
        is_active: Флаг активности — неактивные интеграции пропускаются при синхронизации.
        platform_config: Обновлённые параметры платформы (customer_id, ad_account_id и т.д.).
    """
    name: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None
    platform_config: dict[str, Any] | None = None


# --- Ответы ---

class IntegrationResponse(BaseModel):
    """
    Схема ответа с данными интеграции.
    Токены (access_token, refresh_token) намеренно исключены из ответа.

    Attributes:
        id: UUID интеграции.
        user_id: ID пользователя-владельца интеграции.
        platform: Рекламная платформа.
        name: Название интеграции.
        is_active: Флаг активности интеграции.
        platform_config: Специфичные для платформы параметры.
        created_at: Дата и время создания записи (генерируется БД).
        updated_at: Дата и время последнего обновления записи (генерируется БД).
    """
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
    """
    Схема ответа для списка интеграций пользователя.

    Attributes:
        items: Список интеграций.
        total: Общее количество интеграций пользователя.
    """
    items: list[IntegrationResponse]
    total: int


class OAuthInitRequest(BaseModel):
    """
    Схема запроса для инициализации OAuth-флоу.

    Attributes:
        platform: Рекламная платформа, для которой запрашивается авторизация.
        integration_id: UUID интеграции, к которой привязываются полученные токены.
    """
    platform: PlatformEnum
    integration_id: uuid.UUID


class OAuthInitResponse(BaseModel):
    """
    Схема ответа для инициализации OAuth-флоу.

    Attributes:
        auth_url: Ссылка для редиректа пользователя на страницу авторизации платформы.
    """
    auth_url: str


class OAuthCallbackRequest(BaseModel):
    """
    Схема запроса OAuth callback — вызывается платформой после того,
    как пользователь разрешил доступ.

    Attributes:
        code: Одноразовый авторизационный код для обмена на токены.
        state: Подписанная строка с integration_id для привязки токенов
               к нужной интеграции и защиты от CSRF.
    """
    code: str
    state: str


class TokenStatusResponse(BaseModel):
    """
    Схема ответа для проверки статуса токена интеграции.
    Используется для отображения состояния подключения в интерфейсе
    и диагностики необходимости повторной авторизации.

    Attributes:
        integration_id: UUID проверяемой интеграции.
        is_valid: True если токен существует и не истёк.
        expires_at: Время истечения access_token. None если токен ещё не получен.
    """
    integration_id: uuid.UUID
    is_valid: bool
    expires_at: datetime | None
