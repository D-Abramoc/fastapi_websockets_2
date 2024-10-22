from pathlib import Path

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


settings = Settings()


def get_auth_data():
    return {
        'secret_key': settings.secret,
        'algorithm': settings.algorithm
    }
