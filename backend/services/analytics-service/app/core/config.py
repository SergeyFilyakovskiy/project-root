import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive=True,
        extra='ignore',
    )

    #Redis
    redis_password: SecretStr = Field(validation_alias='redis_password')
    redis_host: str = Field(validation_alias='redis_host')
    redis_port: str = Field(validation_alias='redis_port')
    redis_key: str = Field(validation_alias='redis_key')
    cache_ttl: int = Field(validation_alias='cache_ttl')

    #RabbitMQ
    rabbitmq_user: str = Field(validation_alias='rabbitmq_user')
    rabbitmq_password: SecretStr = Field(validation_alias='rabbitmq_password')
    rabbitmq_host: str = Field(validation_alias='rabbitmq_host')
    rabbitmq_port: int = Field(validation_alias='rabbitmq_port')

    #Clickhouse
    clickhouse_host: str = Field(validation_alias='clickhouse_host')
    clickhouse_port: str = Field(validation_alias='clickhouse_port')
    clickhouse_password: SecretStr = Field(validation_alias='clickhouse_password') 
    clickhouse_user: str = Field(validation_alias='clickhouse_user')
    clickhouse_db: str = Field(validation_alias='clickhouse_db')

    #PostgresSQL
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
    

    def get_redis_url(self):
        return f"redis://:{self.redis_password.get_secret_value()}"\
            f"@{self.redis_host}:{self.redis_port}/{self.redis_key}"

    def get_rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password.get_secret_value()}@"\
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
settings = Config()#type: ignore