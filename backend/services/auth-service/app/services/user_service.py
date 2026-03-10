from fastapi import Cookie, HTTPException
from redis.asyncio import Redis
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import TokenData, UserLoginSchema
from app.core.security import Token, verify_password
from app.models.user import User
from app.repositories.user_repo import UserDAO


async def get_current_user(
    token: str | None = Cookie(default=None, alias="access_token")
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
    postgres_session: AsyncSession,
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
    user = await UserDAO.find_by_email(session=postgres_session, email=login_details.email)

    if user is None:
        return None
    if not verify_password(login_details.password, user):
        return None
    return user

