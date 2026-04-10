from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.messaging.consumer import start_consumer
from app.core.config import settings
from app.core.logging import logger
from app.api.analytics_api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await start_consumer()
    logger.info("[main] analytics-service запущен")
    yield
    await connection.close()

app = FastAPI(
    title="Analytics Service",
    lifespan=lifespan,
    openapi_prefix='/analytics-service',
    version='0.0.1'
)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}