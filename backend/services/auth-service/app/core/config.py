"""

Модуль для загрузки переменных из .env

"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
from pydantic import Field



class DatabaseConfig(BaseSettings):
    """
    
    Класс определяющий все переменные 
    связанные с БД, для того что бы переменна 
    была успешно загружена, она должна начинаться 
    с префикса 'POSTGRES'

    """

    model_config = SettingsConfigDict(
        env_prefix= 'postgres',
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive=True,
        extra= 'ignore'
    )

    postgres_user: str = Field(validation_alias='postgres_user')
    postgres_password: SecretStr = Field(validation_alias='postgres_password')
    postgres_host: str = Field(validation_alias='postgres_host')
    postgres_port: int = Field(validation_alias='postgres_port')
    postgres_db_name: str = Field(validation_alias='postgres_db_name')


    def get_db_async_url(self):
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")

    def get_db_migrations_url(self):
        return (f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")
    
class JWTConfig(BaseSettings):
    """

    Класс определяющий все переменные 
    связанные с JWT, для того что бы переменна 
    была успешно загружена, она должна начинаться 
    с префикса 'JWT'

    """
    model_config = SettingsConfigDict(
        env_prefix='jwt',
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive= True,
        extra='ignore'
    )
    
    jwt_secret: SecretStr = Field(validation_alias='jwt_secret')
    jwt_algorithm: SecretStr = Field(validation_alias='jwt_algorithm')
    
    def get_jwt_secret(self):
        return self.jwt_secret.get_secret_value()
    
    def get_jwt_algorithm(self):
        return self.jwt_algorithm.get_secret_value()

db_config = DatabaseConfig() # type: ignore
jwt_config = JWTConfig()    # type: ignore
