import asyncio
import logging

import aio_pika
import aio_pika.abc

from app.core.config import settings
from app.messaging.schemas import SyncResponseMessage

logger = logging.getLogger(__name__)


class ResponseConsumer:
    """
    Слушает очередь sync.response и раскладывает ответы
    от integration-service по Future-объектам.

    Флоу:
        scheduler публикует запрос - кладёт Future в _pending
        consumer получает ответ - резолвит Future по job_id
        scheduler await'ит Future - получает токен и идёт в коннектор
    """

    def __init__(self, connection: aio_pika.abc.AbstractConnection):
        self.connection = connection
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._pending: dict[str, asyncio.Future] = {}

    async def start(self) -> None:
        """Открывает канал и начинает слушать sync.response."""
        self._channel = await self.connection.channel()
        await self._channel.set_qos(prefetch_count=50)
        queue = await self._channel.declare_queue(
            settings.sync_response_queue,
            durable=True,
        )
        await queue.consume(self._handle_message)
        logger.info("ResponseConsumer started")

    async def stop(self) -> None:
        """Закрывает канал."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

    def register(self, job_id: str) -> asyncio.Future:
        """
        Регистрирует ожидание ответа для job_id.
        Возвращает Future который зарезолвится когда придёт ответ.
        """
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[job_id] = future
        return future


    async def _handle_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        """
        Обрабатывает входящее сообщение — находит Future по job_id
        и резолвит его данными из ответа.
        """
        async with message.process():
            try:
                data = SyncResponseMessage.model_validate_json(message.body)
                job_id = str(data.job_id)
                future = self._pending.pop(job_id, None)

                if future and not future.done():
                    future.set_result(data)
                else:
                    logger.warning(f"No pending future for job_id={job_id}")

            except Exception as e:
                logger.error(f"Failed to handle sync.response: {e}")
