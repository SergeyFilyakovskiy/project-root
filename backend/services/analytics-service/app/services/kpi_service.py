import json
from clickhouse_driver import Client
from redis.asyncio import Redis
from datetime import date
from app.repositories.clickhouse_repo import get_metrics
from app.core.config import settings

async def get_kpi(
    client: Client,
    redis: Redis,
    integration_id: str,
    date_from: date,
    date_to: date,
) -> dict:
    cache_key = f"kpi:{integration_id}:{date_from}:{date_to}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    rows = get_metrics(client, integration_id=integration_id, date_from=date_from, date_to=date_to)

    if not rows:
        return {}

    total_impressions = sum(r["impressions"] for r in rows)
    total_clicks = sum(r["clicks"] for r in rows)
    total_spend = sum(r["spend"] for r in rows)

    kpi = {
        "integration_id": integration_id,
        "date_from": date_from,
        "date_to": date_to,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_spend": round(total_spend, 2),
        "ctr": round(total_clicks / total_impressions * 100, 4) if total_impressions > 0 else 0.0,
        "cpc": round(total_spend / total_clicks, 4) if total_clicks > 0 else 0.0,
        "avg_daily_spend": round(total_spend / len(rows), 2) if rows else 0.0,
    }

    await redis.set(cache_key, json.dumps(kpi), ex=settings.cache_ttl)
    return kpi