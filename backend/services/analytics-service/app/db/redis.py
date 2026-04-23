import redis.asyncio as redis
from redis.asyncio import Redis
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

async def get_redis() -> Redis:
    try:
        redis_client = Redis.from_url(settings.get_redis_url(), decode_responses=True)
        if redis_client is None:
            raise Exception("Failed to connect redis")
        return redis_client  
    except Exception as e:
        raise e
