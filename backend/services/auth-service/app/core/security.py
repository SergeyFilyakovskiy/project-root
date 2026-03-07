"""

Модуль для генерации JWT токенов(access/refresh),
хеширования паролей, проверки паролей

"""

from app.api.schemas import CreateUserRequest, TokenSchema
from app.models.user import User
from app.core.config import jwt_config
from app.db.session import redis_connection

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

    
    refresh_token: str
    access_token: str
    REFRESH_TTL = int(timedelta(days=jwt_config.jwt_refresh_expire).total_seconds())

    def encode_access_token( self, user: User) -> str:
        
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
            self.access_token = access_token
            
            return access_token
        
        except JWTError as e:
            raise e
    
    def encode_refresh_token(self, user: User) -> str:
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
            self.refresh_token = refresh_token\
            
            return f"refresh:{refresh_token}"
        
        except JWTError as e:
            raise e
        
    def decode_token(self, token: TokenSchema) -> dict:
        """
         
         Декодирует токены

         Аргументы:
         - token: TokenSchema - Токен для расшифровки

          Возвращает:
          - dict - Словарь содержащий полезную нагрузку

        """

        return jwt.decode(
            token.token, 
            jwt_config.get_jwt_secret(), 
            algorithms=jwt_config.get_jwt_algorithm()
            )
    
    def user_sessions_key(self, user_id: int)-> str:
        return f"user_sessions:{user_id}"
        

    @redis_connection    
    async def save_refresh_token_in_redis(self, user: User, session: Redis):
        """

        Cохраняет закодированный refresh токен
        в redis

        Аргументы:
        - user: User - Данные о пользователе

        """
        

        async with session.pipeline(transaction=True) as pipe:
            
            try:
                pipe.setex(
                    self.encode_refresh_token(user),
                    self.REFRESH_TTL,
                    str(user.id),
                    )
                pipe.sadd(
                    self.user_sessions_key(user.id),
                    self.refresh_token
                )
                pipe.expire(
                    self.user_sessions_key(user.id),
                    self.REFRESH_TTL
                )
                await pipe.execute()
            except Exception as e:
                raise e
    
    @redis_connection
    async def revoke(self, token: TokenSchema, session: Redis):
        """Отзывает токен при logout"""

        async with session.pipeline(transaction=True) as pipe:
            pipe.delete(f"{token.token_type}:{token.token}")
            
