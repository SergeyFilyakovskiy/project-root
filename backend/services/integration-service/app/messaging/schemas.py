from pydantic import BaseModel
import uuid


class SyncRequestMessage(BaseModel):
    """
    Сообщение от sync-worker с запросом на получение данных.

    Attributes:
        integration_id: UUID интеграции, по которой нужно тянуть данные.
        date_from: Начало периода в формате YYYY-MM-DD.
        date_to: Конец периода в формате YYYY-MM-DD.
    """
    integration_id: uuid.UUID
    date_from: str
    date_to: str


class SyncResponseMessage(BaseModel):
    """
    Ответное сообщение с токеном для выполнения запроса к платформе.

    Attributes:
        integration_id: UUID интеграции.
        access_token: Актуальный токен (обновлённый если был просрочен).
        platform: Название платформы (google_ads / yandex_direct).
        platform_config: Специфичные параметры платформы (customer_id и т.д.).
        success: Успешно ли получен токен.
        error: Сообщение об ошибке если success=False.
    """
    integration_id: uuid.UUID
    access_token: str | None
    platform: str
    platform_config: dict
    success: bool
    error: str | None = None
