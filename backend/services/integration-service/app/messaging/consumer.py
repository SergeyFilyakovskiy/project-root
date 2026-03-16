import json
import aio_pika
from app.core.config import settings
from app.messaging.schemas import SyncRequestMessage, SyncResponseMessage
from app.messaging.publisher import Publisher
from app.repositories.integration_repo import IntegrationRepo
from app.services.token_service import TokenService
from app.core.dependencies import postgres_dependency


class Consumer:
    """
    Слушает очередь запросов от sync-worker'а.
    На каждый запрос получает актуальный токен интеграции
    и публикует ответ обратно в очередь sync.response.
    """
    def __init__(self, connection: aio_pika.abc.AbstractConnection):
        self.connection = connection
        self.publisher = Publisher(connection)
        self._channel = None

    async def start(self) -> None:
        """
        Запускает прослушивание очереди sync.request.
        Вызывается при старте приложения через lifespan.
        """
        self._channel = await self.connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        queue = await self._channel.declare_queue(
                settings.sync_request_queue,
                durable=True,
            )
        await queue.consume(self._handle_message)

    async def stop(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

    async def _handle_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение из очереди.
        В случае любой ошибки публикует ответ с success=False
        вместо того чтобы бросать исключение — это предотвращает
        зависание сообщения в очереди.

        Args:
            message: Входящее сообщение от sync-worker'а.
        """
        async with message.process():
            try:
                data = SyncRequestMessage.model_validate_json(message.body)
                response = await self._process(data)
            except Exception as e:
                response = SyncResponseMessage(
                    integration_id=data.integration_id,
                    access_token=None,
                    platform="",
                    platform_config={},
                    success=False,
                    error=str(e),
                )

            await self.publisher.publish_sync_response(
                queue_name=settings.sync_response_queue,
                message=response,
            )

    async def _process(self, data: SyncRequestMessage, session: postgres_dependency) -> SyncResponseMessage:
        """
        Основная логика обработки запроса:
        получает интеграцию из БД, проверяет и при необходимости
        обновляет токен, возвращает актуальные данные для запроса к платформе.

        Args:
            data: Десериализованное сообщение с integration_id и периодом.

        Returns:
            Сообщение с актуальным токеном и конфигурацией платформы.

        Raises:
            ValueError: Если интеграция не найдена в БД.
        """
        repo = IntegrationRepo(session)
        token_service = TokenService(repo)

        integration = await repo.get_by_id(data.integration_id)
        if not integration:
            raise ValueError(f"Integration {data.integration_id} not found")

        access_token = await token_service.get_valid_token(data.integration_id)

        return SyncResponseMessage(
            integration_id=data.integration_id,
            access_token=access_token,
            platform=integration.platform,
            platform_config=integration.platform_config,
            success=True,
        )
