import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger
from app.db.clickhouse import get_clickhouse_client
from app.db.postgres import get_postgres_connection
from app.db.redis import get_redis_connection
from app.services.kpi_service import get_kpi
from app.services.anomaly_service import detect_and_save_anomalies

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process(requeue=False):  # requeue=True если нужна повторная обработка
        body = json.loads(message.body.decode())
        integration_id = body.get("integration_id")
        date_from = body.get("date_from")
        date_to = body.get("date_to")

        if not integration_id:
            raise ValueError(f"Отсутствует integration_id: {body}")

        logger.info(f"[consumer] Получено событие: integration_id={integration_id}, {date_from}–{date_to}")

        # Клиенты должны быть инициализированными инстансами, не зависимостями
        redis = get_redis_connection()
        clickhouse = get_clickhouse_client()
        postgres = get_postgres_connection()
        
        await get_kpi(
            client=clickhouse,
            redis=redis,
            integration_id=integration_id,
            date_from=date_from,
            date_to=date_to,
        )

        anomalies = await detect_and_save_anomalies(clickhouse, postgres, integration_id)
        if anomalies:
            logger.warning(f"[consumer] Обнаружено аномалий: {len(anomalies)}, integration_id={integration_id}")

async def start_consumer():
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("normalized_data", durable=True)
    await queue.consume(process_message)
    logger.info("[consumer] Слушаем очередь: normalized_data")
    return connection