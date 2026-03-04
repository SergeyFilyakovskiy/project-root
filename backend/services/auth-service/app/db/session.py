"""

Модуль для открытия асинхронного подключения к БД

"""
from datetime import datetime

from sqlalchemy import Integer, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncAttrs
from ..core.config import db_config


#движок для работы с бд
async_engine = create_async_engine(db_config.get_db_async_url())

#Фабрика сессий для взаимодействия с БД
async_session = async_sessionmaker(
    autoflush=False,
    autocommit= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False,
)


#Декоратор позволяющий открывать для любой функции 
#соединение с БД
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally: 
                await session.aclose()

        return wrapper


class Base(AsyncAttrs, DeclarativeBase):
   
    """

    Базовый класс от которого наследуются все
    модели таблиц БД
    Все модели реализованы в /models/user.py

    """
    __abstract__ = True #для того чтобы не создавалась таблица для этого класса
    __table_args__ = {"schema": "auth"}


    id: Mapped[int] =  mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
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