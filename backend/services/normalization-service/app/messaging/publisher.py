import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger

# publisher.py — одно сообщение на весь батч
async def publish_normalized(metrics: list[dict], date_from: str, date_to: str):
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("normalized_data", durable=True)

        payload = {
            "integration_id": metrics[0]["integration_id"],
            "date_from": date_from,
            "date_to": date_to,
            "metrics": metrics,
        }
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload, default=str).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="normalized_data"
        )
        logger.info(f"[publisher] Опубликован батч: {len(metrics)} метрик, {date_from}–{date_to}")