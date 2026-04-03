import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import Boolean, Float, Integer, DateTime, String, UUID ,func

class Base(AsyncAttrs, DeclarativeBase):
   
    """

    Базовый класс от которого наследуются все
    модели таблиц БД

    """
    __abstract__ = True #для того чтобы не создавалась таблица для этого класса
    __table_args__ = {"schema": "analytic"}


    id: Mapped[uuid.UUID] =  mapped_column(
        UUID, 
        primary_key=True, 
        default=uuid.uuid4()
        )
    
    created_at : Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
        )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now()
        )
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'            

class Anomaly(Base):

    """
    Модель аномалии в метриках рекламной кампании.

    Хранит информацию о выявленных отклонениях значений метрик
    от исторической нормы для конкретной интеграции и платформы.

    Поля:
        id (uuid.UUID):
            Уникальный идентификатор записи. Генерируется автоматически.

        integration_id (uuid.UUID):
            Идентификатор интеграции (рекламного аккаунта),
            в метриках которой обнаружена аномалия.

        platform (str):
            Название рекламной платформы (например, "vk", "yandex", "meta").

        metric (str):
            Название метрики, в которой зафиксировано отклонение.
            Возможные значения: "ctr", "spend", "clicks".

        date (datetime):
            Дата, за которую зафиксировано аномальное значение метрики.

        expected (float):
            Ожидаемое (среднее историческое) значение метрики
            на основе данных за предшествующий период.

        actual (float):
            Фактическое значение метрики в аномальную дату.

        deviation (float):
            Отклонение фактического значения от ожидаемого, в процентах.
            Вычисляется как abs(actual - expected) / expected * 100.

        is_resolved (bool):
            Флаг устранения аномалии. False — аномалия активна,
            True — аномалия рассмотрена и помечена как решённая.
            По умолчанию: False.

        created_at (datetime):
            Дата и время создания записи. Устанавливается автоматически.

        updated_at (datetime):
            Дата и время последнего обновления записи.
            Обновляется автоматически при изменении.
    """
  
    integration_id : Mapped[uuid.UUID] = mapped_column(
        UUID, 
        nullable=False,
        )
    
    platform: Mapped[str] = mapped_column(
        String, 
        nullable=False
        )
    
    metric: Mapped[str] = mapped_column(
        String, 
        nullable=False
        )       # "ctr", "spend", "clicks"
    
    date: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False
        )
    
    expected: Mapped[float] = mapped_column(
        Float, 
        nullable=False
        )
    
    actual: Mapped[float] = mapped_column(
        Float, 
        nullable=False
        )
    
    deviation: Mapped[float] = mapped_column(
        Float,
        nullable=False
        )
    
    is_resolved: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
        )
