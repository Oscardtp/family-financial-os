"""FastAPI dependency for per-endpoint rate limiting."""
from typing import Annotated
from fastapi import Depends, HTTPException, Request
from app.core.rate_limit import RateLimitTier
from app.core.rate_limit_service import RateLimitService

_service = RateLimitService()


def RateLimitDependency(tier: RateLimitTier):
    """Create a dependency that enforces rate limiting for a specific tier."""

    async def _check(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        key = f"{tier.value}:{client_ip}"
        allowed, retry_after = _service.check(key, tier)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

    return Depends(_check)
