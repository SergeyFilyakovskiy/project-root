import redis.asyncio as redis
from redis.asyncio import Redis
from fastapi import Depends
from typing import Annotated
from app.core.config import settings

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
            await session.aclose()


redis_pool = redis.ConnectionPool.from_url(
    settings.get_redis_url(),
    decode_responses = True,
    max_connections = 20,
)

redis_dependency = Annotated[Redis, Depends(get_redis_connection)]

async def get_redis() -> Redis:
    return Redis.from_url(settings.get_redis_url(), decode_responses=True)