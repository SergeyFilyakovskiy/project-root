from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_dao import BaseDAO
from app.models.anomaly import Anomaly

class AnomalyRepo(BaseDAO):
    """
    
    Все базовые CRUD реализованы в BaseDAO
    При необходимости можно будет добавить тут

    """
    model = Anomaly
