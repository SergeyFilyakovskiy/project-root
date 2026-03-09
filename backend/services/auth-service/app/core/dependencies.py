"""
Модуль со всеми зависимостями 
"""

from app.db.session import get_postgres_connection, get_redis_connection
from app.services.role_service import RoleChecker
from app.api.schemas import RoleEnum, TokenData
from app.services.user_service import get_current_user


from fastapi import Depends
from typing import Annotated, Sequence
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession


#Зависимости для пользователя
CurrentUser = Annotated[TokenData, Depends(get_current_user)]

#Зависимости для сессий в БД
postgres_dependency = Annotated[AsyncSession, Depends(get_postgres_connection)]

redis_dependency = Annotated[Redis,Depends(get_redis_connection)]


#Зависимости для ролей
admin_only = Annotated[Sequence[str],Depends(RoleChecker([RoleEnum.ADMIN]))]

manager_or_admin = Annotated[Sequence[str],Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.ADMIN]))]
