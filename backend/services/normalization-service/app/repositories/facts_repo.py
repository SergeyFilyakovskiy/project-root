from clickhouse_driver import Client
from app.messaging.schemas import NormalizedMetric

from datetime import datetime

def insert_metrics(client: Client, metrics: list[NormalizedMetric]):
    rows = [
        (
            datetime.strptime(m.date, "%Y-%m-%d").date(),  # ← str → date
            m.integration_id, m.platform,
            m.campaign_group, m.campaign_id, m.campaign_name,
            m.impressions, m.clicks, m.spend,
            m.currency, m.ctr, m.cpc,
        )
        for m in metrics
    ]
    client.execute("INSERT INTO facts_metrics VALUES", rows)


def get_metrics(
    client: Client,
    integration_id: str | None = None,
    platform: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    conditions = []
    params = {}

    if integration_id:
        conditions.append("integration_id = %(integration_id)s")
        params["integration_id"] = integration_id
    if platform:
        conditions.append("platform = %(platform)s")
        params["platform"] = platform
    if date_from:
        conditions.append("date >= %(date_from)s")
        params["date_from"] = date_from
    if date_to:
        conditions.append("date <= %(date_to)s")
        params["date_to"] = date_to

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM facts_metrics {where} ORDER BY date DESC"

    rows = client.execute(query, params, with_column_types=True)
    data, columns = rows, client.execute(
        f"SELECT * FROM facts_metrics {where} LIMIT 0", params, with_column_types=True
    )
    
    results = client.execute(query, params, with_column_types=False)
    cols = [
        "date", "integration_id", "platform", "campaign_group",
        "campaign_id", "campaign_name", "impressions", "clicks",
        "spend", "currency", "ctr", "cpc"
    ]
    return [dict(zip(cols, row)) for row in results] # type: ignore