"""

Модуль для загрузки переменных из .env

"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
from pydantic import Field


class BaseConfig(BaseSettings):
    """

    Базовый класс настройки загрузок

    """
    model_config = SettingsConfigDict(
        env_file= os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), 
        env_file_encoding='utf-8',
        extra= 'ignore',
    )

class DatabaseConfig(BaseConfig):
    """
    
    Класс определяющий все переменные 
    связанные с БД, для того что бы переменна 
    была успешно загружена, она должна начинаться 
    с префикса 'POSTGRES'

    """

    model_config = SettingsConfigDict(
        env_prefix= 'POSTGRES',
    )

    POSTGRES_USER : str
    POSTGRES_PASSWORD : SecretStr
    POSTGRES_DB : str
    POSTGRES_HOST: str
    POSTGRES_PORT:  int
    POSTGRES_DB_NAME: str

    def get_db_async_url(self):
        return (f"postgresql+async://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB_NAME}")

    def get_db_migrations_url(self):
        return (f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB_NAME}")    
    
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
    
    def get_jwt_secret(self):
        return self.jwt_secret.get_secret_value()
    
    def get_jwt_algorithm(self):
        return self.jwt_algorithm.get_secret_value()

class Config(BaseSettings):

    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)

    @classmethod
    def load(cls):
        return cls()
    