"""
Модуль со всеми зависимостями 
"""

from app.db.session import get_postgres_connection, get_redis_connection
from app.api.schemas import TokenData
from app.services.user_service import get_current_user

from fastapi import Depends
from typing import Annotated
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession


#Зависимости для пользователя
CurrentUser = Annotated[TokenData, Depends(get_current_user)]

#Зависимости для сессий в БД
postgres_dependency = Annotated[AsyncSession, Depends(get_postgres_connection)]

redis_dependency = Annotated[Redis,Depends(get_redis_connection)]


