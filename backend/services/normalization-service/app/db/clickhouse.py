from clickhouse_driver import Client
from app.core.config import settings

def get_clickhouse_client() -> Client:
    return Client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_db,
        user=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )

def ensure_table_exists():
    client = get_clickhouse_client()
    client.execute("""
        CREATE TABLE IF NOT EXISTS facts_metrics (
            date             Date,
            integration_id   String,
            platform         String,
            campaign_group   String,
            campaign_id      String,
            campaign_name    String,
            impressions      UInt64,
            clicks           UInt64,
            spend            Float64,
            currency         String,
            ctr              Float64,
            cpc              Float64
        )
        ENGINE = MergeTree()
        ORDER BY (date, integration_id, platform, campaign_id)
    """)