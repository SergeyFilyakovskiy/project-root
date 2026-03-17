import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger

async def publish_task(queue_name: str, payload: dict):
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )
        logger.info(f"[publisher] Опубликовано в '{queue_name}': integration_id={payload.get('integration_id')}")
