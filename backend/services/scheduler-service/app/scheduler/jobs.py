import httpx
from app.core.config import settings
from app.core.logging import logger
from app.messaging.publisher import publish_task

async def fetch_and_publish_integrations():
    logger.info("[jobs] Запуск: получение активных интеграций...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.integration_service_url}/integrations/internal/",
                headers={"X-Service-Key": settings.service_key.get_secret_value()},
                timeout=10.0,
            )
            response.raise_for_status()
            integrations = response.json()["items"]
    except Exception as e:
        logger.error(f"[jobs] Не удалось получить интеграции: {e}")
        return

    logger.info(f"[jobs] Получено интеграций: {len(integrations)}")

    for integration in integrations:
        payload = {
            "integration_id": integration["id"],
            "platform": integration["platform"],
        }
        await publish_task(queue_name="sync_jobs", payload=payload)

    logger.info(f"[jobs] Опубликовано задач: {len(integrations)}")
