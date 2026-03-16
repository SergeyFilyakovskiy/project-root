import logging

import aio_pika

from app.messaging.schemas import SyncRequestMessage

logger = logging.getLogger(__name__)


class RequestPublisher:
    """
    Публикует запрос токена в sync.request для integration-service.
    """

    def __init__(self, connection: aio_pika.abc.AbstractConnection):
        self.connection = connection

    async def publish(self, message: SyncRequestMessage, queue_name: str) -> None:
        """
        Args:
            message: Запрос с job_id, integration_id и периодом.
            queue_name: Имя очереди из settings.sync_request_queue.
        """
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message.model_dump_json().encode(),
                    content_type="application/json",
                ),
                routing_key=queue_name,
            )
            logger.info(f"Published sync.request for job_id={message.job_id}")
