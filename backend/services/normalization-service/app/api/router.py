from fastapi import APIRouter, Query, Depends
from app.api.schemas import MetricsListResponse
from app.repositories.facts_repo import get_metrics
from app.db.clickhouse import get_clickhouse_client

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/", response_model=MetricsListResponse)
async def list_metrics(
    integration_id: str | None = Query(default=None),
    platform: str | None = Query(default=None),
    date_from: str | None = Query(default=None),  # "YYYY-MM-DD"
    date_to: str | None = Query(default=None),
):
    client = get_clickhouse_client()
    items = get_metrics(
        client,
        integration_id=integration_id,
        platform=platform,
        date_from=date_from,
        date_to=date_to,
    )
    return MetricsListResponse(items=items, total=len(items)) # type: ignore