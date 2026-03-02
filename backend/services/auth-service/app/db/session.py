"""

Модуль для открытия асинхронного подключения к БД

"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi import Depends
from typing import Annotated
from ..core.config import Config

db_url = Config.load().db.db_url.get_secret_vaule()

async_engine = create_async_engine(db_url)

async_session = async_sessionmaker(
    autoflush=False,
    autocommit= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False,
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.aclose()

db_dependency = Annotated[AsyncSession, Depends(get_db)]
