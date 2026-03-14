from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
import redis.asyncio as redis 

#движок для работы с бд
async_engine = create_async_engine(settings.get_db_async_url())

#Фабрика сессий для взаимодействия с БД
async_session = async_sessionmaker(
    autoflush=False,
    autocommit= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False,
)

async def get_postgres_connection():
    """
    Генератор для подключения к Postgres

    Передает:
    - session - Сессия в postgres
    """
    async with async_session() as session:
        try:        
            yield session
        except Exception as e:
            await session.rollback()
            raise e     
        finally: 
            await session.aclose()


redis_pool = redis.ConnectionPool.from_url(
    settings.get_redis_url(),
    decode_responses = True,
    max_connections = 20,
)

async def get_redis_connection():
    """
    Генератор для подключения к Redis

    Передает:
    - session - Сессия в redis
    """
    async with redis.Redis(connection_pool=redis_pool) as session:
        try:
            yield session
        except Exception as e:
            raise e
        finally:
            await session.close()

