from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.messaging.consumer import start_consumer
from app.db.clickhouse import ensure_table_exists
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_table_exists()
    connection = await start_consumer()
    logger.info("[main] normalization-service запущен")
    yield
    await connection.close()

app = FastAPI(title="Normalization Service", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}