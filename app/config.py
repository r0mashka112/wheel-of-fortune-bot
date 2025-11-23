from pathlib import Path
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    REDIS_HOST: str

    BOT_TOKEN: str
    BASE_SITE: str

    CHAT_ID: int

    @property
    def DATABASE_URL_AIOMYSQL(self) -> str:
        return (f'mysql+aiomysql://'
            f'{self.DB_USER}:'
            f'{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:'
            f'{self.DB_PORT}/'
            f'{self.DB_NAME}'
        )

    @property
    def DATABASE_URL_AIOREDIS(self) -> str:
        return f'redis://{self.REDIS_HOST}'

    @property
    def WEBHOOK_URL(self) -> str:
        return f'{self.BASE_SITE}/webhook'

    model_config = SettingsConfigDict(
        env_file = str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding = 'utf-8'
    )

settings = Settings()