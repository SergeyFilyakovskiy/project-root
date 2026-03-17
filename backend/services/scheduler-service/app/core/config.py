import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        case_sensitive=True,
        extra="ignore",
    )

    # RabbitMQ
    sync_jobs_queue: str = "sync.jobs"
    rabbitmq_user: str = Field(validation_alias='rabbitmq_user')
    rabbitmq_password: SecretStr = Field(validation_alias='rabbitmq_password')
    rabbitmq_host: str = Field(validation_alias='rabbitmq_host')
    rabbitmq_port: int = Field(validation_alias='rabbitmq_port')

    integration_service_url: str = "http://nginx/integration-service"
    sync_interval_seconds: int = 3600 

    service_key: SecretStr = Field(validation_alias='service_key')


    def get_rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password.get_secret_value()}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )


settings = Settings() # type: ignore
