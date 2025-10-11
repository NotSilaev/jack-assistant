from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str

    class Config:
        env_file = Path(__file__).parent / ".env"


settings = Settings()
