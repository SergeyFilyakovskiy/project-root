import asyncio
import logging

import aio_pika

from app.core.config import settings
from app.core.logging import setup_logging
from app.messaging.consumer import ResponseConsumer
from app.messaging.consumer_jobs import JobsConsumer

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())

    response_consumer = ResponseConsumer(connection)
    await response_consumer.start()

    jobs_consumer = JobsConsumer(connection, response_consumer)
    await jobs_consumer.start()

    logger.info("sync-worker started")

    try:
        await asyncio.Future()  # висим бесконечно
    finally:
        await jobs_consumer.stop()
        await response_consumer.stop()
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
