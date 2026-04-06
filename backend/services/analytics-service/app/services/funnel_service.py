from datetime import date
from clickhouse_driver import Client
from app.repositories.clickhouse_repo import get_metrics

def get_funnel(
    client: Client,
    integration_id: str,
    date_from: date,
    date_to: date,
) -> dict:
    rows = get_metrics(client, integration_id=integration_id, date_from=date_from, date_to=date_to)

    if not rows:
        return {}

    total_impressions = sum(r["impressions"] for r in rows)
    total_clicks = sum(r["clicks"] for r in rows)
    total_spend = sum(r["spend"] for r in rows)

    return {
        "stages": [
            {"name": "Показы", "value": total_impressions},
            {"name": "Клики", "value": total_clicks},
        ],
        "conversion_rate": round(total_clicks / total_impressions * 100, 4) if total_impressions > 0 else 0.0,
        "cost_per_click": round(total_spend / total_clicks, 4) if total_clicks > 0 else 0.0,
    }