from typing import Annotated

from fastapi import Cookie, HTTPException, Depends
from redis.asyncio import Redis
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import TokenData, TokenSchema, UserLoginSchema
from app.core.security import Token, verify_password
from app.models.user import User
from app.repositories.user_repo import UserDAO


async def get_current_user(
    token: str | None = Cookie(default=None, alias="access")
) -> TokenData:
    """
    Извлекает и валидирует JWT access токен из cookie.

    Аргументы:
    - token: str | None - JWT токен из cookie 'access'

    Возвращает:
    - TokenData - данные пользователя из токена

    Исключения:
    - HTTPException 401 если токен отсутствует или невалиден

    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не аутентифицирован",
        )
    return Token.get_token_payload(token)


async def authenticate_user(
    login_details: UserLoginSchema,
    session: AsyncSession,
) -> User | None:
    """
    Аутентифицирует пользователя по email и паролю.

    Аргументы:
    - login_details: UserLoginSchema - email и пароль пользователя
    - session: AsyncSession - асинхронная сессия базы данных

    Возвращает:
    - User если аутентификация успешна
    - None если пользователь не найден или пароль неверный

    """
    user = await UserDAO.find_by_email(session=session, email=login_details.email)

    if user is None:
        return None
    if not verify_password(login_details.password, user):
        return None
    return user


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
