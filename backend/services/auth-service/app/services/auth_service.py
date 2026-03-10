from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.schemas import TokenSchema
from app.core.security import Token
from app.repositories.user_repo import UserDAO

async def refresh_access_token(
    refresh_token: str,
    redis_session: Redis,
    postgres_session: AsyncSession,
) -> str:
    """
    Обновляет access токен по refresh токену.

    Аргументы:
    - refresh_token: str - JWT refresh токен из cookie
    - session: AsyncSession - асинхронная сессия базы данных

    Возвращает:
    - str - новый JWT access токен

    Исключения:
    - HTTPException 401 если refresh токен невалиден или не найден в Redis

    """
    token = Token()

    user_id = Token.get_user_id_from_refresh(refresh_token)

    refresh_token_schema = TokenSchema(
        token=refresh_token,
        token_type='refresh'
    )

    is_valid = await token.is_valid(refresh_token_schema, redis_session)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен недействителен или истёк"
        )

    user = await UserDAO.find_by_id(postgres_session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )


    await token.revoke(refresh_token_schema, redis_session)  
    new_access_token = token.encode_access_token(user)
    await token.save_refresh_token_in_redis(user, redis_session)

    return new_access_token
