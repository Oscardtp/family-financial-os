"""Global rate limiting middleware for FastAPI."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.rate_limit import RateLimitTier
from app.core.rate_limit_service import RateLimitService

_rate_limit_service = RateLimitService()

HEALTH_PATHS = {"/health", "/docs", "/openapi.json"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global middleware that applies READ-tier limits to all requests."""

    async def dispatch(self, request: Request, call_next):
        from app.config import get_settings
        settings = get_settings()

        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        if request.url.path in HEALTH_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        tier = RateLimitTier.READ
        key = f"global:{tier.value}:{client_ip}"

        allowed, retry_after = _rate_limit_service.check(key, tier)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
