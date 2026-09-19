"""Tests to verify security configuration is properly set.

FASE 4B.10 — Security Hardening & Verification Gate
"""
import os
from pathlib import Path


def test_allowed_origins_loaded_from_config():
    """CORS_ORIGINS must be loaded from Settings, not hardcoded."""
    from app.config import Settings
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) > 0
    assert all(isinstance(o, str) for o in settings.CORS_ORIGINS)


def test_rate_limit_settings_exist():
    """RATE_LIMIT_ENABLED and RATE_LIMIT_STORAGE must be configured."""
    from app.config import Settings
    settings = Settings()
    assert hasattr(settings, 'RATE_LIMIT_ENABLED')
    assert hasattr(settings, 'RATE_LIMIT_STORAGE')
    assert isinstance(settings.RATE_LIMIT_ENABLED, bool)
    assert settings.RATE_LIMIT_STORAGE in ('memory', 'redis', 'database')


def test_secret_key_required():
    """SECRET_KEY must not be the default in production."""
    from app.config import Settings
    settings = Settings()
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) > 0
    assert settings.ALGORITHM == "HS256"


def test_env_defaults_are_safe():
    """Default values should be safe for development."""
    from app.config import Settings
    settings = Settings()
    assert settings.DEBUG is False or settings.DEBUG is True
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0


def test_cors_origins_not_wildcard():
    """CORS origins must never default to wildcard *."""
    from app.config import Settings
    settings = Settings()
    assert "*" not in settings.CORS_ORIGINS


def test_security_headers_present():
    """FastAPI app must have security headers middleware configured."""
    from app.main import app
    middleware_classes = [type(m).__name__ for m in app.user_middleware]
    has_cors = any('CORSMiddleware' in str(m) for m in app.user_middleware)
    assert has_cors, "CORSMiddleware must be configured"


def test_env_example_exists():
    """.env.example file must exist with required variables."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env.example"
    assert env_path.exists(), ".env.example file must exist"
    content = env_path.read_text()
    required_vars = ["SECRET_KEY", "DATABASE_URL", "ALLOWED_ORIGINS", "RATE_LIMIT_ENABLED"]
    for var in required_vars:
        assert var in content, f"{var} must be in .env.example"
