"""

Модуль для генерации JWT токенов(access/refresh),
хеширования паролей, проверки паролей

"""

from app.api.schemas import UserRegisterSchema, TokenSchema, TokenData
from app.models.user import User
from app.core.config import jwt_config
from app.core.dependencies import redis_dependency

from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from redis.asyncio import Redis
from starlette import status

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

def hash_password(user: UserRegisterSchema) -> str:
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
            'role': user.role,
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
            
            return refresh_token
        
        except JWTError as e:
            raise e
    
    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
         
         Декодирует токены

         Аргументы:
         - token: TokenSchema - Токен для расшифровки

          Возвращает:
          - dict - Словарь содержащий полезную нагрузку

        """

        return jwt.decode(
            token, 
            jwt_config.get_jwt_secret(), 
            algorithms=[jwt_config.get_jwt_algorithm()]
            )
    
    @classmethod
    def user_sessions_key(cls, user_id: int)-> str:
        return f"user_sessions:{user_id}"
        
   
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
    
    @classmethod
    async def revoke(cls, token: TokenSchema, session: Redis):
        """
        Отзывает токен при logout

        Аргументы:
        - token: TokenSchema - Токен для отзыва

        """
        payload = cls.decode_token(token.token)
        user_id = payload.get("sub")

        async with session.pipeline(transaction=True) as pipe:
            try:
                pipe.delete(f"{token.token_type}:{token.token}")
                if user_id:
                    pipe.srem(
                        cls.user_sessions_key(user_id),
                        token.token
                    )
                await pipe.execute()
            except Exception as e:
                raise e


    @classmethod
    async def is_valid(cls, token: TokenSchema, session: Redis) -> bool:
        """
        Проверяет существует ли токен в Redis

        Аргументы:
        - token: TokenSchema - Токен для проверки

        Возвращает:
        - bool - True если токен валиден

        """
        result = await session.exists(
            f"{token.token_type}:{token.token}"
        )
        return bool(result)

    
    @classmethod
    async def get_user_id_by_token(
        cls, token: TokenSchema, session: Redis
    ) -> int | None:
        """
        Возвращает user_id по refresh токену из Redis

        Аргументы:
        - token: TokenSchema - Токен для поиска

        Возвращает:
        - int | None - ID пользователя или None

        """
        value = await session.get(
            f"{token.token_type}:{token.token}"
        )
        return int(value) if value else None

    @classmethod
    def get_token_payload(cls, token: str) -> TokenData:
        """
        Декодирует access токен и возвращает данные пользователя.

        Аргументы:
        - token: str - JWT access токен

        Возвращает:
        - TokenData - данные пользователя из токена

        Исключения:
        - HTTPException 401 если токен невалиден или не является access токеном

        """
        try:
            payload = cls.decode_token(token)

            if payload.get('type') != 'access':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип токена"
                )

            user_id = payload.get('id')
            user_email = payload.get('sub')
            user_role = payload.get('role')

            if user_id is None or user_email is None or user_role is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Не удалось валидировать токен"
                )

            return TokenData(id=user_id, email=user_email, role=user_role)

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось валидировать токен"
            ) from e
        
    @classmethod
    def get_user_id_from_refresh(cls, token: str) -> int:
        """
        Декодирует refresh токен и возвращает ID пользователя.
        Используется при обновлении access токена.

        Аргументы:
        - token: str - JWT refresh токен

        Возвращает:
        - int - ID пользователя

        Исключения:
        - HTTPException 401 если токен невалиден или не является refresh токеном

        """
        try:
            payload = cls.decode_token(token)

            if payload.get('type') != 'refresh':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип токена"
                )

            user_id = payload.get('sub')
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Не удалось валидировать токен"
                )

            return int(user_id)

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось валидировать токен"
            ) from e
    
