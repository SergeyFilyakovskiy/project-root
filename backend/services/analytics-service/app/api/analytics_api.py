from datetime import date
from fastapi import APIRouter, Query, Depends
from app.core.dependencies import postgres_dependency, clickhouse_dependency, redis_dependency
from app.services.kpi_service import get_kpi
from app.services.comparison_service import compare_periods, compare_platforms
from app.services.funnel_service import get_funnel
from app.repositories.anomaly_repo import AnomalyRepo

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpi")
async def kpi(
    click: clickhouse_dependency,
    redis: redis_dependency,
    integration_id: str = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
):

    return await get_kpi(click, redis, integration_id, date_from, date_to)


@router.get("/funnel")
async def funnel(
    click: clickhouse_dependency,
    integration_id: str = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return get_funnel(click, integration_id, date_from, date_to)


@router.get("/compare/periods")
async def compare_periods_endpoint(
    click: clickhouse_dependency,
    integration_id: str = Query(...),
    period_a_from: date = Query(...),
    period_a_to: date = Query(...),
    period_b_from: date = Query(...),
    period_b_to: date = Query(...),
):
    return compare_periods(
        click, integration_id,
        (period_a_from, period_a_to),
        (period_b_from, period_b_to),
    )


@router.get("/compare/platforms")
async def compare_platforms_endpoint(
    click: clickhouse_dependency,
    integration_id: str = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
): 
    return compare_platforms(click, integration_id, date_from, date_to)


@router.get("/anomalies")
async def anomalies(
    postgres: postgres_dependency,
    integration_id: str | None = Query(default=None),
    is_resolved: bool | None = Query(default=None),
):
    return await AnomalyRepo.all_anomalies_for_integration(
        postgres,
        integration_id,
        is_resolved,
    )