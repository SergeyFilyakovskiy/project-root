import json
import aio_pika
from app.core.config import settings
from app.messaging.schemas import SyncResponseMessage


class Publisher:
    
    """
    Публикует сообщения в очереди RabbitMQ.
    Используется для отправки ответов в sync-worker
    после получения/обновления токена интеграции.
    """

    def __init__(self, connection: aio_pika.abc.AbstractConnection):
        self.connection = connection

    async def publish_sync_response(
        self,
        queue_name: str,
        message: SyncResponseMessage,
    ) -> None:
        """
        Публикует ответ на запрос синхронизации в указанную очередь.

        Args:
            queue_name: Имя очереди назначения (например, "sync.response").
            message: Объект ответа с токеном и данными платформы.
        """
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message.model_dump_json().encode(),
                    content_type="application/json",
                ),
                routing_key=queue_name,
            )
