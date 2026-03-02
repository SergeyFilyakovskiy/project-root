"""

Модуль для загрузки переменных из .env

"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
from pydantic import Field


class BaseConfig(BaseSettings):
    """

    Базовый класс настройки загрузок

    """
    model_config = SettingsConfigDict(
        env_file= '.env', 
        env_file_encoding='utf-8',
        extra= 'ignore',
    )

class DatabaseConfig(BaseConfig):
    """
    
    Класс определяющий все переменные 
    связанные с БД, для того что бы переменна 
    была успешно загружена, она должна начинаться 
    с префикса 'db'

    """

    model_config = SettingsConfigDict(
        env_prefix= 'db'
    )

    db_url: SecretStr
    db_migrations_url: SecretStr

class JWTConfig(BaseConfig):
    """

    Класс определяющий все переменные 
    связанные с JWT, для того что бы переменна 
    была успешно загружена, она должна начинаться 
    с префикса 'jwt'

    """
    model_config = SettingsConfigDict(
        env_prefix='jwt'
    )
    
    jwt_secret: SecretStr
    jwt_algorithm: SecretStr

class Config(BaseSettings):

    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)

    @classmethod
    def load(cls) -> Config:
        return cls()
    