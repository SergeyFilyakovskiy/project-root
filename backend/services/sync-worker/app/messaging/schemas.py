import uuid

from pydantic import BaseModel
from datetime import datetime

from enum import StrEnum

class SyncStatus(StrEnum):
    PENDING = "pending"       # создана, ещё не отправлена
    IN_PROGRESS = "in_progress"  # запрос отправлен в RabbitMQ
    SUCCESS = "success"       # данные успешно получены
    FAILED = "failed"         # ошибка при синхронизации

class SyncJobMessage(BaseModel):
    """
    Сообщение от scheduler-service.
    Приходит в очередь sync.jobs — сигнал запустить синхронизацию.
    """
    job_id: uuid.UUID
    integration_id: uuid.UUID
    platform: str
    date_from: datetime
    date_to: datetime

class SyncRequestMessage(BaseModel):
    """
    Сообщение запроса токена у integration-service.
    Публикуется scheduler'ом в очередь sync.request.
    """
    job_id: uuid.UUID
    integration_id: uuid.UUID
    date_from: datetime
    date_to: datetime

class SyncResponseMessage(BaseModel):
    """
    Ответ от integration-service с токеном и конфигом платформы.
    Приходит в очередь sync.response.
    """
    job_id: uuid.UUID
    integration_id: uuid.UUID
    access_token: str | None
    platform: str
    platform_config: dict
    success: bool
    error: str | None = None