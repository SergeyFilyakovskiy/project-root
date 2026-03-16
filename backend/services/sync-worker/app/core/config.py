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

    #Настройки Postgres
    postgres_user: str = Field(validation_alias='postgres_user')
    postgres_password: SecretStr = Field(validation_alias='postgres_password')
    postgres_host: str = Field(validation_alias='postgres_host')
    postgres_port: int = Field(validation_alias='postgres_port')
    postgres_db_name: str = Field(validation_alias='postgres_db_name')

    #RabbitMQ
    sync_request_queue: str = "sync.request"
    sync_response_queue: str = "sync.response"
    sync_jobs_queue: str = "sync.jobs"
    rabbitmq_user: str = Field(validation_alias='rabbitmq_user')
    rabbitmq_password: SecretStr = Field(validation_alias='rabbitmq_password')
    rabbitmq_host: str = Field(validation_alias='rabbitmq_host')
    rabbitmq_port: int = Field(validation_alias='rabbitmq_port')

    def get_rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password.get_secret_value()}@"\
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"

    def get_db_async_url(self):
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")

    def get_db_migrations_url(self):
        return (f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password.get_secret_value()}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}")
    

settings = Settings() # type: ignore
