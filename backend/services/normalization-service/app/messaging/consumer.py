import json
import aio_pika
from app.core.config import settings
from app.core.logging import logger
from app.messaging.schemas import NormalizedBatchMessage, RawDataMessage
from app.services.normalizer import normalize
from app.services.currency_service import get_exchange_rates, convert_to_base
from app.services.time_zone_service import to_utc
from app.db.clickhouse import get_clickhouse_client
from app.repositories.facts_repo import insert_metrics
from app.db.redis import get_redis
from app.messaging.publisher import publish_normalized

async def process_message(
        message: aio_pika.abc.AbstractIncomingMessage,
        ):
    async with message.process():
        redis = await get_redis()
        try:
            body = json.loads(message.body.decode())
            raw_message = RawDataMessage(**body)
            logger.info(
                "[consumer] Получено: platform=%s integration=%s %s–%s",
                raw_message.platform,
                raw_message.integration_id,
                raw_message.date_from,
                raw_message.date_to,
            )

            metrics = normalize(raw_message)

            rates = await get_exchange_rates(redis=redis)
            for m in metrics:
                m.spend = convert_to_base(m.spend, m.currency, rates)
                m.cpc = round(m.spend / m.clicks, 4) if m.clicks > 0 else 0.0
                m.currency = "USD"

            for m in metrics:
                m.date = to_utc(m.date)

            client = get_clickhouse_client()
            insert_metrics(client, metrics)
            logger.info(
                "[consumer] Записано %s строк в ClickHouse",
                len(metrics),
            )

            batch = NormalizedBatchMessage(
                integration_id=raw_message.integration_id,
                platform=raw_message.platform,
                date_from=raw_message.date_from,
                date_to=raw_message.date_to,
                metrics=metrics,
            )
            await publish_normalized(batch)

        except Exception as e:
            logger.error(f"[consumer] Ошибка обработки: {e}")

        finally:
            await redis.aclose()


async def start_consumer():
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("raw_data", durable=True)
    await queue.consume(process_message)
    logger.info("[consumer] Слушаем очередь: raw_data")
    return connection