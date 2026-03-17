import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    
    Класс для загрузки настроек из  .env

    """

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive=True,
        extra="ignore",
    )

    #Настройки для google
    google_client_id: str = Field(validation_alias='google_client_id')
    google_client_secret: SecretStr = Field(validation_alias='google_client_secret')
    google_redirect_uri: str = Field(validation_alias='redirect_uri')

    #Настройки для yandex
    yandex_client_id: str = Field(validation_alias='yandex_client_id')
    yandex_client_secret: SecretStr = Field(validation_alias='yandex_client_secret')
    yandex_redirect_uri: str = Field(validation_alias='redirect_uri')

    #Настройки для meta 
    # meta_client_id: str = Field(validation_alias='META_CLIENT_ID')
    # meta_client_secret: SecretStr = Field(validation_alias='META_CLIENT_SECRET')
    # met_redirect_uri: str = Field(validation_alias='redirect_uri')

    #Настройки Postgres
    postgres_user: str = Field(validation_alias='postgres_user')
    postgres_password: SecretStr = Field(validation_alias='postgres_password')
    postgres_host: str = Field(validation_alias='postgres_host')
    postgres_port: int = Field(validation_alias='postgres_port')
    postgres_db_name: str = Field(validation_alias='postgres_db_name')

    #Настройки типов
    db_encryption_key: SecretStr = Field(validation_alias='db_encryption_key')

    #Redis
    redis_password: SecretStr = Field(validation_alias='redis_password')
    redis_host: str = Field(validation_alias='redis_host')
    redis_port: int = Field(validation_alias='redis_port')
    redis_db: str = Field(validation_alias='redis_db')

    #RabbitMQ
    sync_request_queue: str = "sync.request"
    sync_response_queue: str = "sync.response"
    rabbitmq_user: str = Field(validation_alias='rabbitmq_user')
    rabbitmq_password: SecretStr = Field(validation_alias='rabbitmq_password')
    rabbitmq_host: str = Field(validation_alias='rabbitmq_host')
    rabbitmq_port: int = Field(validation_alias='rabbitmq_port')

    service_key: SecretStr = Field(validation_alias='service_key')

    def get_rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password.get_secret_value()}@"\
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
    def get_redis_url(self):
        return f"redis://:{self.redis_password.get_secret_value()}"\
        f"@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_db_async_url(self):
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")

    def get_db_migrations_url(self):
        return (f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")
    

settings = Settings() # type: ignore
