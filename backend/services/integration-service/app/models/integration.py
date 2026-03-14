import uuid
from datetime import datetime
from sqlalchemy import JSON, Boolean, Integer, String, func, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs

from app.db.types import EncryptedString

class Base(AsyncAttrs, DeclarativeBase):
   
    """

    Базовый класс от которого наследуются все
    модели таблиц БД

    """
    __abstract__ = True #для того чтобы не создавалась таблица для этого класса
    __table_args__ = {"schema": "integrations"}


    id: Mapped[uuid.UUID] =  mapped_column( 
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

class Integration(Base):


    user_id: Mapped[int] = mapped_column(
        nullable=False, 
        index=True
        )
    
    platform: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
        )
    
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
        )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
        )

    access_token: Mapped[str | None] = mapped_column(
        EncryptedString, 
        nullable=True
        )
    
    refresh_token: Mapped[str | None] = mapped_column(
        EncryptedString, 
        nullable=True
        )
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
        )

    platform_config: Mapped[dict] = mapped_column(
        JSON, 
        default=dict
        )
