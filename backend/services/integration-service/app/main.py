import aio_pika
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.router import router
from app.messaging.consumer import Consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await aio_pika.connect_robust(settings.get_rabbitmq_url())
    consumer = Consumer(connection)
    await consumer.start()

    yield

    await consumer.stop()
    await connection.close()



app = FastAPI(
    title="Integration Service",
    root_path="/integration-service",
    lifespan=lifespan
)


app.include_router(router)
