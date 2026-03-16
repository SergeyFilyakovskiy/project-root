import asyncio
import logging

import aio_pika
import aio_pika.abc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.messaging.schemas import SyncJobMessage, SyncRequestMessage, SyncStatus
from app.messaging.publisher import RequestPublisher
from app.messaging.consumer import ResponseConsumer
from app.connectors.google_ads import GoogleAdsConnector
from app.connectors.yandex_direct import YandexDirectConnector
from app.repositories.sync_jpb_repo import SyncJobRepo
from app.db.session import async_session

logger = logging.getLogger(__name__)

CONNECTORS: dict = {
    "google_ads": GoogleAdsConnector,
    "yandex_direct": YandexDirectConnector,
}  # заполним когда напишем коннекторы


class JobsConsumer:
    """
    Слушает sync.jobs от scheduler-service.
    На каждый job:
        1. Запрашивает токен у integration-service через RabbitMQ
        2. Ждёт ответ через ResponseConsumer
        3. Вызывает нужный коннектор
    """

    def __init__(
        self,
        connection: aio_pika.abc.AbstractConnection,
        response_consumer: ResponseConsumer,
    ):
        self.connection = connection
        self.response_consumer = response_consumer
        self.publisher = RequestPublisher(connection)
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def start(self) -> None:
        self._channel = await self.connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        queue = await self._channel.declare_queue(
            settings.sync_jobs_queue,
            durable=True,
        )
        await queue.consume(self._handle_message)
        logger.info("JobsConsumer started")

    async def stop(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

    async def _handle_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        async with message.process():
            try:
                job = SyncJobMessage.model_validate_json(message.body)
                await self._process(job)
            except Exception as e:
                logger.error(f"JobsConsumer error: {e}")

    async def _process(self, job: SyncJobMessage) -> None:
        async with async_session() as db:
            try:
                await self._run(job, db)
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                await db.aclose()

    async def _run(self, job: SyncJobMessage, db: AsyncSession) -> None:
        """
        Основная логика обработки job.

        Args:
            job: Сообщение от scheduler-service с данными задачи.
            db: Сессия базы данных.
        """
        repo = SyncJobRepo(db)

        sync_job = await repo.create(
            integration_id=job.integration_id,
            platform=job.platform,
            date_from=job.date_from,
            date_to=job.date_to,
        )
        await repo.set_status(sync_job.id, SyncStatus.IN_PROGRESS)

        try:
            future = self.response_consumer.register(str(sync_job.id))

            await self.publisher.publish(
                SyncRequestMessage(
                    job_id=sync_job.id,
                    integration_id=job.integration_id,
                    date_from=job.date_from,
                    date_to=job.date_to,
                ),
                queue_name=settings.sync_request_queue,
            )

            response = await asyncio.wait_for(future, timeout=30.0)

            if not response.success:
                raise ValueError(response.error or "integration-service error")

            connector_class = CONNECTORS.get(response.platform)
            if connector_class is None:
                raise ValueError(f"Unknown platform: {response.platform}")

            connector = connector_class(
                access_token=response.access_token,
                config=response.platform_config,
            )
            await connector.fetch(date_from=job.date_from, date_to=job.date_to)

            await repo.set_status(sync_job.id, SyncStatus.SUCCESS)

        except asyncio.TimeoutError:
            await repo.set_status(sync_job.id, SyncStatus.FAILED, error="Timeout")

        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            await repo.set_status(sync_job.id, SyncStatus.FAILED, error=str(e))