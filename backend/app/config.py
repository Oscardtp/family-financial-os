from pathlib import Path
import warnings
from pydantic_settings import BaseSettings
from functools import lru_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_FILE = PROJECT_ROOT / "family_financial.db"


class Settings(BaseSettings):
    APP_NAME: str = "Family Financial OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = ""
    DATABASE_SYNC_URL: str = ""

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.DATABASE_URL:
        settings.DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE}"
        settings.DATABASE_SYNC_URL = f"sqlite:///{DB_FILE}"
    if settings.SECRET_KEY == "change-me-in-production":
        if not settings.DEBUG:
            raise RuntimeError(
                "SECRET_KEY must be set in .env for production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        warnings.warn(
            "SECRET_KEY is using the default value. "
            "Set SECRET_KEY in your .env file for production.",
            stacklevel=2,
        )
    return settings
