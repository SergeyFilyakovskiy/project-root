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
        integration_id: str, 
        is_resloved: bool,
        limit: int = 100, 
        offset: int = 10,
    ):
        result = await db.execute(
            select(Anomaly)
            .where(Anomaly.integration_id == integration_id)
            .where(Anomaly.is_resolved == is_resloved)
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

