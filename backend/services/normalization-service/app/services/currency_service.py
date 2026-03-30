import json
import httpx
from redis.asyncio import Redis
from app.core.logging import logger
from app.core.config import settings

BASE_CURRENCY = "USD"
FALLBACK_RATES = {"USD": 1.0, "RUB": 0.011, "BYN": 0.31, "EUR": 1.08}


def _update_fallback_cache(rates: dict[str, float]) -> None:
    FALLBACK_RATES.update({
        k: v for k, v in rates.items() if k in FALLBACK_RATES
    })
    logger.info("[currency] Курсы успешно обновлены")

async def get_exchange_rates(redis: Redis) -> dict[str, float]:
    cached = await redis.get(settings.redis_key)
    if cached:
        logger.info("[currency] Курсы взяты из Redis")
        return json.loads(cached)

    rates = await _fetch_from_api()
    _update_fallback_cache(rates)
    await redis.set(settings.redis_key, json.dumps(rates), ex=settings.cache_ttl)
    logger.info("[currency] Курсы получены из API и закэшированы в Redis")
    return rates


async def _fetch_from_api() -> dict[str, float]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}",
                timeout=5.0,
            )
            return response.json().get("rates", FALLBACK_RATES)
    except Exception as e:
        logger.warning(f"[currency] API недоступен, fallback: {e}")
        return FALLBACK_RATES


def convert_to_base(amount: float, currency: str, rates: dict[str, float]) -> float:
    rate = rates.get(currency, 1.0)
    return round(amount / rate, 4)