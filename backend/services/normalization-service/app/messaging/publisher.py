import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger
from app.messaging.schemas import NormalizedBatchMessage


async def publish_normalized(batch: NormalizedBatchMessage):
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("normalized_data", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=batch.model_dump_json().encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
            ),
            routing_key="normalized_data",
        )
        logger.info(
            "[publisher] Опубликован батч: %s метрик, %s–%s",
            len(batch.metrics),
            batch.date_from,
            batch.date_to,
        )