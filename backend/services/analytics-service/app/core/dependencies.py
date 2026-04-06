from app.db.clickhouse import get_clickhouse_client
from app.db.postgres import get_postgres_connection
from app.db.redis import get_redis_connection

from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from clickhouse_driver import Client


postgres_dependency = Annotated[AsyncSession, Depends(get_postgres_connection)]

redis_dependency = Annotated[Redis, Depends(get_redis_connection)]

clickhouse_dependency = Annotated[Client, Depends(get_clickhouse_client)]
