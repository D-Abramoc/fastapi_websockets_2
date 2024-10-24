from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Chat'
    description: str = 'Chat'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    algorithm: str = ''

    min_password_length: int = 3
    max_length_string: int = 100
    min_length_string: int = 1
    base_dir: Path = Path(__file__).parent.parent.parent

    host: str = 'localhost'
    model_config = SettingsConfigDict(env_file='infra/.env', extra="ignore")


class BotSettings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='infra/.env', extra="ignore")


settings = Settings()
bot_settings = BotSettings()


def get_auth_data():
    return {
        'secret_key': settings.secret,
        'algorithm': settings.algorithm
    }


templates = Jinja2Templates(directory="templates")
