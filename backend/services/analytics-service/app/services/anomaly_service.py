from datetime import datetime
from clickhouse_driver import Client
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.clickhouse_repo import get_metrics_for_anomaly
from app.repositories.anomaly_repo import AnomalyRepo

METRICS_TO_CHECK = ["ctr", "spend", "clicks"]
DEVIATION_THRESHOLD = 50.0  # процент отклонения для аномалии

async def detect_and_save_anomalies(
    client: Client,
    db: AsyncSession,
    integration_id: str,
) -> list[dict]:
    detected = []

    for metric in METRICS_TO_CHECK:
        rows = get_metrics_for_anomaly(client, integration_id, metric, days=30)
        if len(rows) < 7:
            continue

        values = [r["value"] for r in rows[1:]]  # исторические (без последнего)
        latest = rows[0]

        avg = sum(values) / len(values)
        if avg == 0:
            continue

        deviation = abs(latest["value"] - avg) / avg * 100

        if deviation >= DEVIATION_THRESHOLD:
            anomaly_data = {
                "integration_id": integration_id,
                "platform": "unknown",
                "metric": metric,
                "date": latest["date"],
                "expected": round(avg, 4),
                "actual": round(latest["value"], 4),
                "deviation": round(deviation, 2),
                "detected_at": datetime.utcnow(),
                "is_resolved": False,
            }
            await AnomalyRepo.add(db, anomaly_data)
            detected.append(anomaly_data)

    return detected