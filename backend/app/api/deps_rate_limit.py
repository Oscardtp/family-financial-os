"""FastAPI dependency for per-endpoint rate limiting."""
from fastapi import HTTPException, Request
from app.core.rate_limit import RateLimitTier
from app.presentation.middleware.rate_limit import _rate_limit_service as _service


def RateLimitDependency(tier: RateLimitTier):
    """Create a dependency callable that enforces rate limiting for a specific tier.

    Usage: Depends(RateLimitDependency(tier=RateLimitTier.AUTH))
    """

    async def _check(request: Request):
        from app.config import get_settings
        settings = get_settings()
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_ip = request.client.host if request.client else "unknown"
        key = f"{tier.value}:{client_ip}"
        allowed, retry_after = _service.check(key, tier)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

    return _check
