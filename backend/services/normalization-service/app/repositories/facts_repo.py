from clickhouse_driver import Client
from app.api.schemas import NormalizedMetric

def insert_metrics(client: Client, metrics: list[NormalizedMetric]):
    rows = [
        (
            m.date,
            m.integration_id,
            m.platform,
            m.campaign_group,
            m.campaign_id,
            m.campaign_name,
            m.impressions,
            m.clicks,
            m.spend,
            m.currency,
            m.ctr,
            m.cpc,
        )
        for m in metrics
    ]
    client.execute(
        "INSERT INTO facts_metrics VALUES",
        rows,
    )