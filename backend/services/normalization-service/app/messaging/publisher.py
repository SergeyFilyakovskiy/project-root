import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger

async def publish_normalized(metrics: list[dict]):
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("normalized_data", durable=True)

        for metric in metrics:
            await channel.default_exchange.publish(
                        aio_pika.Message(
                            body= json.dumps(metric, default=str).encode(),
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                        ),
                        routing_key="normalized_data"
                    )
            logger.info(f"[publisher] Опубликовано {len(metrics)} записей в 'normalized_data'")
            

