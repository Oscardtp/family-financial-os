"""Rate Limiting infrastructure tests (TDD - GREEN phase).

These tests verify that the rate limiting middleware and dependency
correctly enforce request limits per tier and return proper 429 responses.
"""
import os
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def app_with_rate_limiting():
    from fastapi import FastAPI
    from app.presentation.middleware.rate_limit import RateLimitMiddleware, _rate_limit_service
    from app.presentation.error_handlers import register_rate_limit_handler
    from app.config import get_settings

    _rate_limit_service.clear()

    # Enable rate limiting for this test app
    get_settings.cache_clear()
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    get_settings.cache_clear()

    test_app = FastAPI()
    register_rate_limit_handler(test_app)
    test_app.add_middleware(RateLimitMiddleware)

    @test_app.get("/health")
    async def health():
        return {"status": "ok"}

    @test_app.get("/test-read")
    async def test_read():
        return {"data": "ok"}

    @test_app.post("/test-write")
    async def test_write():
        return {"data": "created"}

    @test_app.get("/test-auth")
    async def test_auth():
        return {"data": "auth"}

    yield test_app

    # Restore disabled state for other tests
    os.environ["RATE_LIMIT_ENABLED"] = "false"
    get_settings.cache_clear()
    _rate_limit_service.clear()


@pytest.fixture
def client(app_with_rate_limiting):
    transport = ASGITransport(app=app_with_rate_limiting, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture(autouse=True)
def clear_rate_limit_store():
    from app.presentation.middleware.rate_limit import _rate_limit_service
    _rate_limit_service.clear()
    yield
    _rate_limit_service.clear()


async def test_requests_under_limit_succeed(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200


async def test_rate_limit_returns_429_when_exceeded(client: AsyncClient):
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier

    config = TIER_CONFIGS[RateLimitTier.READ]
    for _ in range(config.requests + 2):
        response = await client.get("/test-auth")

    assert response.status_code == 429


async def test_retry_after_header_exists(client: AsyncClient):
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier

    config = TIER_CONFIGS[RateLimitTier.READ]
    for _ in range(config.requests + 1):
        response = await client.get("/test-auth")

    assert response.status_code == 429
    assert "retry-after" in response.headers


async def test_limit_resets_after_window(client: AsyncClient):
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier

    config = TIER_CONFIGS[RateLimitTier.READ]
    for _ in range(config.requests + 1):
        await client.get("/test-auth")

    response = await client.get("/test-auth")
    assert response.status_code == 429

    from app.presentation.middleware.rate_limit import _rate_limit_service
    _rate_limit_service.clear()

    response = await client.get("/test-auth")
    assert response.status_code == 200


# ============================================================
# Auth Rate Limiting Tests (FASE 4B.3)
# ============================================================

@pytest.fixture
def auth_app():
    """Create app with real auth router + rate limiting enabled."""
    from fastapi import FastAPI
    from app.presentation.v1.auth import router as auth_router
    from app.presentation.middleware.rate_limit import RateLimitMiddleware, _rate_limit_service
    from app.presentation.error_handlers import register_rate_limit_handler
    from app.database import get_db
    from app.config import get_settings
    from tests.conftest import override_get_db

    get_settings.cache_clear()
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    get_settings.cache_clear()
    _rate_limit_service.clear()

    test_app = FastAPI()
    test_app.dependency_overrides[get_db] = override_get_db
    register_rate_limit_handler(test_app)
    test_app.add_middleware(RateLimitMiddleware)
    test_app.include_router(auth_router, prefix="/api/v1")

    yield test_app

    os.environ["RATE_LIMIT_ENABLED"] = "false"
    get_settings.cache_clear()
    _rate_limit_service.clear()


@pytest.fixture
def auth_client(auth_app):
    transport = ASGITransport(app=auth_app, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture(autouse=True)
def _clear_all_rate_limit_stores():
    from app.presentation.middleware.rate_limit import _rate_limit_service
    from app.api.deps_rate_limit import _service
    _rate_limit_service.clear()
    _service.clear()
    yield
    _rate_limit_service.clear()
    _service.clear()


async def test_login_rate_limit_429(auth_client: AsyncClient):
    """6th login attempt should return 429."""
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier
    config = TIER_CONFIGS[RateLimitTier.AUTH]

    payload = {"email": "nonexistent@test.com", "password": "wrongpass"}
    for i in range(config.requests):
        resp = await auth_client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code != 429, f"Request {i+1} should not be 429"

    resp = await auth_client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 429


async def test_register_rate_limit_429(auth_client: AsyncClient):
    """Register exceeding limit should return 429."""
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier
    config = TIER_CONFIGS[RateLimitTier.AUTH]

    for i in range(config.requests):
        payload = {"email": f"user_{i}@test.com", "password": "Test1234!"}
        resp = await auth_client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code != 429, f"Request {i+1} should not be 429"

    payload = {"email": "user_overflow@test.com", "password": "Test1234!"}
    resp = await auth_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 429


async def test_refresh_rate_limit_429(auth_client: AsyncClient):
    """Refresh exceeding limit should return 429."""
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier
    config = TIER_CONFIGS[RateLimitTier.AUTH]

    for i in range(config.requests):
        resp = await auth_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": f"fake_token_{i}"}
        )
        assert resp.status_code != 429, f"Request {i+1} should not be 429"

    resp = await auth_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "fake_overflow"}
    )
    assert resp.status_code == 429


async def test_auth_retry_after_header(auth_client: AsyncClient):
    """429 on auth must include Retry-After header."""
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier
    config = TIER_CONFIGS[RateLimitTier.AUTH]

    payload = {"email": "nonexistent@test.com", "password": "wrong"}
    for _ in range(config.requests + 1):
        resp = await auth_client.post("/api/v1/auth/login", json=payload)

    assert resp.status_code == 429
    assert "retry-after" in resp.headers


async def test_different_ips_have_independent_limits():
    """Different client IPs should have independent rate limit buckets."""
    from app.core.rate_limit import TIER_CONFIGS, RateLimitTier
    from app.core.rate_limit_service import RateLimitService

    config = TIER_CONFIGS[RateLimitTier.AUTH]
    service = RateLimitService()

    for i in range(config.requests):
        allowed_a, _ = service.check("auth:192.168.1.1", RateLimitTier.AUTH)
        assert allowed_a, f"IP A request {i+1} should be allowed"

    allowed_a, _ = service.check("auth:192.168.1.1", RateLimitTier.AUTH)
    assert not allowed_a, "IP A should be rate limited"

    for i in range(config.requests):
        allowed_b, _ = service.check("auth:10.0.0.1", RateLimitTier.AUTH)
        assert allowed_b, f"IP B request {i+1} should be allowed"
