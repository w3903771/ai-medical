from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Medical Backend"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    sqlite_url: str = "sqlite+aiosqlite:///./medical.sqlite3"
    log_level: str = "INFO"
    log_format: Optional[str] = None

    class Config:
        env_file = ".env"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings