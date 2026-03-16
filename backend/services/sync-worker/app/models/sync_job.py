
import uuid
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import String, Text, func, DateTime, UUID, Enum

from app.messaging.schemas import SyncStatus

class Base(DeclarativeBase, AsyncAttrs):
    """

    Базовый класс от которого наследуются все
    модели таблиц БД

    """
    __abstract__ = True #для того чтобы не создавалась таблица для этого класса
    __table_args__ = {"schema": "sync"}


    id: Mapped[uuid.UUID] =  mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4,
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
    

class SyncJob(Base):

    integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False, 
        index= True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(SyncStatus),
        nullable=False,
        default=SyncStatus.PENDING,
    )

    date_from: Mapped[datetime] = mapped_column(
        DateTime(timezone= True),
        nullable=False,
    )

    date_to: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    

