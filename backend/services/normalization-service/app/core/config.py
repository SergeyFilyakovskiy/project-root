import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive=True,
        extra='ignore',
    )

    #Clickhouse
    clickhouse_host: str = Field(validation_alias='clickhouse_host')
    clickhouse_port: str = Field(validation_alias='clickhouse_port')
    clickhouse_password: SecretStr = Field(validation_alias='clickhouse_password') 
    clickhouse_user: str = Field(validation_alias='clickhouse_user')
    clickhouse_db: str = Field(validation_alias='clickhouse_db')

    #RabbitMQ
    rabbitmq_user: str = Field(validation_alias='rabbitmq_user')
    rabbitmq_password: SecretStr = Field(validation_alias='rabbitmq_password')
    rabbitmq_host: str = Field(validation_alias='rabbitmq_host')
    rabbitmq_port: int = Field(validation_alias='rabbitmq_port')

    #Redis
    redis_password: SecretStr = Field(validation_alias='redis_password')
    redis_host: str = Field(validation_alias='redis_host')
    redis_port: str = Field(validation_alias='redis_port')
    redis_key: str = Field(validation_alias='redis_key')
    cache_ttl: int = Field(validation_alias='cache_ttl')

    def get_redis_url(self):
        return f"redis://:{self.redis_password.get_secret_value()}"\
        f"@{self.redis_host}:{self.redis_port}/{self.redis_key}"

    def get_rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password.get_secret_value()}@"\
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"


settings = Config()#type: ignore