
from clickhouse_driver import Client

COLUMNS = [
    'date', 'integration_id', 'platform', 'campaign_group',
    'campaign_id', 'campaign_name', 'impressions', 'clicks',
    'spend', 'currency', 'ctr', 'cpc'
]

def get_metrics(
        client: Client,
        integration_id: str | None = None,
        platform: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 1000,
        offset: int = 0
)-> list[dict]:
    
    conditions, params = [], {}

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
    rows = client.execute(
        f"SELECT {', '.join(COLUMNS)} FROM facts_metrics \
            {where} ORDER BY date DESC\
            LIMIT {limit} OFFSET {offset}",
        params,
    )
    return [dict(zip(COLUMNS, row)) for row in rows]  # type: ignore


ALLOWED_METRICS = {"ctr", "spend", "clicks", "impressions", "cpc"}

def get_metrics_for_anomaly(
    client: Client,
    integration_id: str,
    metric: str,
    days: int = 30,
) -> list[dict]:
    if metric not in ALLOWED_METRICS:
        raise ValueError(f"Недопустимая метрика: {metric}")
    
    rows = client.execute(
    f"SELECT date, {metric}, platform FROM facts_metrics "
    "WHERE integration_id = %(integration_id)s "
    "AND date >= today() - %(days)s "
    "ORDER BY date DESC",
    {"integration_id": integration_id, "days": days}
    )
    return [{"date": r[0], "value": r[1], "platform": r[2]} for r in rows] # type: ignore