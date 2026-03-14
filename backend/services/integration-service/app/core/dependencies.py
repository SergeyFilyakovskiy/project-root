from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Header, HTTPException
from typing import Annotated


from app.db.session import get_postgres_connection, get_redis_connection


postgres_dependency = Annotated[AsyncSession, Depends(get_postgres_connection)]

redis_dependency = Annotated[Redis, Depends(get_redis_connection)]

async def get_current_user_id(x_user_id: int = Header(None)) -> int:
    if x_user_id is None:
        raise HTTPException(401, "Unauthorized")
    return x_user_id


user_dependency = Annotated[int, Depends(get_current_user_id)]


