from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base_dao import BaseDAO
from app.models.anomaly import Anomaly

class AnomalyRepo(BaseDAO):
    """
    
    Все базовые CRUD реализованы в BaseDAO
    При необходимости можно будет добавить тут

    """
    model = Anomaly

    @classmethod
    async def all_anomalies_for_integration(
        cls,
        db: AsyncSession,
        integration_id: str | None = None,
        is_resolved: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        query = select(Anomaly)

        if integration_id is not None:
            query = query.where(Anomaly.integration_id == integration_id)

        if is_resolved is not None:
            query = query.where(Anomaly.is_resolved == is_resolved)

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

