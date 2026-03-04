"""

Модуль для генерации JWT токенов(access/refresh),
хеширования паролей, проверки паролей

"""

from app.api.schemas import CreateUserRequest
from app.models.user import User
from app.core.config import jwt_config

from .config import JWTConfig
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from redis.asyncio import Redis

bcrypt_context = CryptContext(
    schemes=['bcrypt'],
    decprecated = 'auto',
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl='auth/token',
)

def verify_password(password: str, user: User) -> bool:
    """
    
    Проверяет на соответствие пароль, который ввели 
    с паролем соответствующего пользователя из БД

    Аргументы:
    - password: str - пароль для проверки
    - user: User - данные о пользователе из БД

    Возвращает:
    - bool - Статус проверки

    """
    return bcrypt_context.verify(password, user.hashed_password)

def hash_password(user: CreateUserRequest) -> str:
    """
    
    Хеширует пароль для записи в БД

    Аргументы:
    - user: CreateUserRequest - объект класса запроса на создание 
    пользователя

    Возвращает:
    - str - захешированный пароль

    """
    return bcrypt_context.hash(user.password)

class Token:

    @classmethod
    def create_access_token( cls, user: User) -> str:
        
        """
        Создает jwt access токен

        Аргументы:
        - user: User - данные о пользователе из БД

        Возвращает:
        - str - Готовый закодированный токен

        """
        
        expires = datetime.now(timezone.utc) \
            + timedelta(minutes=jwt_config.jwt_access_expire)

        payload = {
            'sub': user.email,
            'id': user.id,
            'type': 'access',
            'exp': expires,
        }

        try:
            access_token = jwt.encode(
                                payload, 
                                jwt_config.get_jwt_secret(), 
                                algorithm= jwt_config.get_jwt_algorithm()
                            )
            return access_token
        
        except JWTError as e:
            raise e
    
    @classmethod
    def create_refresh_token(cls, user: User) -> str:
        """
        Создает refresh токен

        Аргументы:
        - user: User - данные о пользователе из БД

        Возвращает:
        - str - Готовый закодированный токен

        """
        expires = datetime.now(timezone.utc)\
            + timedelta(days=jwt_config.jwt_refresh_expire)

        payload = {
            'sub': user.id,
            'type': 'refresh',
            'exp': expires,
        }

        try:
            refresh_token = jwt.encode(
                                payload, 
                                jwt_config.get_jwt_secret(), 
                                algorithm= jwt_config.get_jwt_algorithm()
                            )
            return refresh_token
        
        except JWTError as e:
            raise e
        
