
from clickhouse_driver import Client
from app.repositories.clickhouse_repo import get_metrics

def get_funnel(
    client: Client,
    integration_id: str,
    date_from: str,
    date_to: str,
) -> list:
    rows = get_metrics(client, integration_id=integration_id, date_from=date_from, date_to=date_to)

    if not rows:
        return []

    total_impressions = sum(r["impressions"] for r in rows)
    total_clicks = sum(r["clicks"] for r in rows)

    return [
        {"name": "Показы", "value": total_impressions},
        {"name": "Клики", "value": total_clicks},
    ]