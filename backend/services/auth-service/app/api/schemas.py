"""
    Module with Pydantic schemas for request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ========================
#       ENUMS
# ========================

class RoleEnum(str):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


class TokenTypeEnum(str):
    ACCESS = 'access'
    REFRESH = 'refresh'


# ========================
#       TOKEN
# ========================

class TokenSchema(BaseModel):
    """
    Схема токена.

    Поля:
    - token: str - закодированный JWT токен
    - token_type: str - тип токена (access/refresh)

    """

    token: str
    token_type: str


class TokenResponseSchema(BaseModel):
    """
    Схема ответа после успешной аутентификации.

    Поля:
    - access_token: str - закодированный JWT access токен
    - token_type: str - тип токена, всегда 'bearer'

    """

    access_token: str
    token_type: str = "bearer"


# ========================
#       PROFILE
# ========================

class ProfileCreateSchema(BaseModel):
    """
    Схема для создания профиля пользователя.

    Поля:
    - username: str - уникальное имя пользователя (3-30 символов)
    - first_name: str - имя пользователя (1-50 символов)
    - last_name: str | None - фамилия пользователя (необязательно)
    - date_of_birth: datetime - дата рождения пользователя

    """

    username: str = Field(min_length=3, max_length=30)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    date_of_birth: datetime

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: datetime) -> datetime:
        if v >= datetime.now():
            raise ValueError('Дата рождения не может быть в будущем')
        return v


class ProfileUpdateSchema(BaseModel):
    """
    Схема для обновления профиля пользователя.
    Все поля опциональны — обновляются только переданные.

    Поля:
    - username: str | None - новое имя пользователя
    - first_name: str | None - новое имя
    - last_name: str | None - новая фамилия
    - date_of_birth: datetime | None - новая дата рождения

    """

    username: str | None = Field(default=None, min_length=3, max_length=30)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    date_of_birth: datetime | None = None


class ProfileResponseSchema(BaseModel):
    """
    Схема ответа с данными профиля.

    Поля:
    - id: int - идентификатор профиля
    - username: str - имя пользователя
    - first_name: str - имя
    - last_name: str | None - фамилия
    - date_of_birth: datetime - дата рождения
    - created_at: datetime - дата создания профиля

    """

    id: int
    username: str
    first_name: str
    last_name: str | None
    date_of_birth: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ========================
#       USER
# ========================

class UserRegisterSchema(BaseModel):
    """
    Схема для регистрации нового пользователя.

    Поля:
    - email: EmailStr - электронная почта
    - password: str - пароль (8-50 символов)
    - username: str - имя пользователя (3-30 символов)
    - first_name: str - имя (1-50 символов)
    - last_name: str | None - фамилия (необязательно)
    - date_of_birth: datetime - дата рождения

    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    username: str = Field(min_length=3, max_length=30)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    date_of_birth: datetime


class UserLoginSchema(BaseModel):
    """
    Схема для входа пользователя.

    Поля:
    - email: EmailStr - электронная почта
    - password: str - пароль

    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=50)


class UserResponseSchema(BaseModel):
    """
    Схема ответа с полными данными пользователя.

    Поля:
    - id: int - идентификатор пользователя
    - email: str - электронная почта
    - role: str - роль пользователя
    - profile: ProfileResponseSchema - данные профиля
    - created_at: datetime - дата регистрации

    """

    id: int
    email: str
    role: str
    profile: ProfileResponseSchema
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRoleSchema(BaseModel):
    """
    Схема для обновления роли пользователя (только для админа).

    Поля:
    - user_id: int - идентификатор пользователя
    - role: str - новая роль (admin/manager/user)

    """

    user_id: int
    role: str


class UserChangePasswordSchema(BaseModel):
    """
    Схема для смены пароля пользователя.

    Поля:
    - old_password: str - текущий пароль
    - new_password: str - новый пароль (8-50 символов)

    """

    old_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)
