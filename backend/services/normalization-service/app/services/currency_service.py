import httpx
from app.core.logging import logger

BASE_CURRENCY = "USD"

FALLBACK_RATES = {
    "USD": 1.0,
    "RUB": 0.011,
    "BYN": 0.31,
    "EUR": 1.08,
}

async def _fetch_rates_from_api() -> dict[str, float] | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}",
            timeout=5.0,
        )
        return response.json().get("rates")

def _update_fallback_cache(rates: dict[str, float]) -> None:
    FALLBACK_RATES.update({
        k: v for k, v in rates.items() if k in FALLBACK_RATES
    })
    logger.info("[currency] Курсы успешно обновлены")

async def get_exchange_rates() -> dict[str, float]:
    try:
        rates = await _fetch_rates_from_api()
        if rates:
            _update_fallback_cache(rates)
        return rates or FALLBACK_RATES
    except Exception as e:
        logger.warning(f"[currency] Не удалось получить курсы, используем fallback: {e}")
        return FALLBACK_RATES