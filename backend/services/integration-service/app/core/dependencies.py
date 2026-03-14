from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from app.db.session import get_postgres_connection, get_redis_connection


postgres_dependency = Annotated[AsyncSession, Depends(get_postgres_connection)]

redis_dependency = Annotated[Redis, Depends(get_redis_connection)]

 