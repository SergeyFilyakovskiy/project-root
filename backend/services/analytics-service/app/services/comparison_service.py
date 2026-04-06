from datetime import date
from clickhouse_driver import Client
from app.repositories.clickhouse_repo import get_metrics

def compare_periods(
    client: Client,
    integration_id: str,
    period_a: tuple[date, date],
    period_b: tuple[date, date],
) -> dict:
    def aggregate(rows):
        if not rows:
            return {}
        impressions = sum(r["impressions"] for r in rows)
        clicks = sum(r["clicks"] for r in rows)
        spend = sum(r["spend"] for r in rows)
        return {
            "impressions": impressions,
            "clicks": clicks,
            "spend": round(spend, 2),
            "ctr": round(clicks / impressions * 100, 4) if impressions > 0 else 0.0,
            "cpc": round(spend / clicks, 4) if clicks > 0 else 0.0,
        }

    rows_a = get_metrics(client, integration_id=integration_id, date_from=period_a[0], date_to=period_a[1])
    rows_b = get_metrics(client, integration_id=integration_id, date_from=period_b[0], date_to=period_b[1])

    agg_a = aggregate(rows_a)
    agg_b = aggregate(rows_b)

    delta = {}
    for key in agg_a:
        if agg_a[key] and agg_b.get(key):
            delta[key] = round((agg_b[key] - agg_a[key]) / agg_a[key] * 100, 2)
        else:
            delta[key] = None

    return {"period_a": agg_a, "period_b": agg_b, "delta_percent": delta}


def compare_platforms(
    client: Client,
    integration_id: str,
    date_from: date,
    date_to: date,
) -> list[dict]:
    rows = get_metrics(client, integration_id=integration_id, date_from=date_from, date_to=date_to)

    by_platform: dict[str, list] = {}
    for r in rows:
        by_platform.setdefault(r["platform"], []).append(r)

    result = []
    for platform, platform_rows in by_platform.items():
        impressions = sum(r["impressions"] for r in platform_rows)
        clicks = sum(r["clicks"] for r in platform_rows)
        spend = sum(r["spend"] for r in platform_rows)
        result.append({
            "platform": platform,
            "impressions": impressions,
            "clicks": clicks,
            "spend": round(spend, 2),
            "ctr": round(clicks / impressions * 100, 4) if impressions > 0 else 0.0,
            "cpc": round(spend / clicks, 4) if clicks > 0 else 0.0,
        })
    return result