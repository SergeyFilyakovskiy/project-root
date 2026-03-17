from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.jobs import fetch_and_publish_integrations
from app.core.config import settings
from app.core.logging import logger

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        fetch_and_publish_integrations,
        trigger="interval",
        seconds=settings.sync_interval_seconds,
        id="fetch_and_publish",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[main] Планировщик запущен")
    yield
    scheduler.shutdown()
    logger.info("[main] Планировщик остановлен")

app = FastAPI(
    title="Scheduler Service", 
    lifespan=lifespan,
    root_path="/scheduler-service",
    )

@app.get("/health")
async def health():
    jobs = scheduler.get_jobs()
    return {
        "status": "ok",
        "jobs": [{"id": j.id, "next_run": str(j.next_run_time)} for j in jobs],
    }

@app.post("/trigger")
async def trigger():
    await fetch_and_publish_integrations()
    return {"status": "triggered"}