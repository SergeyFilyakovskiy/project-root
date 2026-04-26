from clickhouse_driver import Client
from app.repositories.clickhouse_repo import get_metrics


def get_timeseries(
    client: Client,
    integration_id: str,
    date_from: str,
    date_to: str,
) -> list:
    rows = get_metrics(client, integration_id=integration_id, date_from=date_from, date_to=date_to)

    if not rows:
        return []

    # Группируем по дате (на случай если get_metrics вернёт несколько строк за один день)
    by_date: dict = {}
    for r in rows:
        d = str(r["date"])
        if d not in by_date:
            by_date[d] = {"date": d, "clicks": 0, "impressions": 0, "spend": 0.0}
        by_date[d]["clicks"] += r["clicks"]
        by_date[d]["impressions"] += r["impressions"]
        by_date[d]["spend"] += r["spend"]

    result = sorted(by_date.values(), key=lambda x: x["date"])

    for row in result:
        row["spend"] = round(row["spend"], 2)

    return result