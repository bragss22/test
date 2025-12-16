from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://app:secret@postgres:5432/orders'
    REDIS_URL: str = 'redis://redis:6379/0'
    RABBITMQ_URL: str = 'amqp://guest:guest@rabbitmq:5672/'
    SECRET_KEY: str = Field(default='your-very-secret-key-minimum-32-characters-long', min_length=32)
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ['http://localhost', 'http://localhost:8000']

    class Config:
        env_file = '.env'
        case_sensitive = False
        env_prefix = 'APP_'
        extra = 'ignore'


settings = Settings()
