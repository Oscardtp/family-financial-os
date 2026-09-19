"""Rate Limiting service.

Manages request counting per client key with sliding window logic.
Storage-agnostic: uses in-memory dict by default, ready for Redis swap.
"""
import time
from dataclasses import dataclass, field
from app.core.rate_limit import RateLimitConfig, RateLimitTier, TIER_CONFIGS


@dataclass
class _Bucket:
    count: int = 0
    window_start: float = field(default_factory=time.time)


class RateLimitService:
    """In-memory rate limit service with per-key sliding windows."""

    def __init__(self) -> None:
        self._store: dict[str, _Bucket] = {}

    def check(
        self, key: str, tier: RateLimitTier
    ) -> tuple[bool, int]:
        """Check if request is allowed.

        Returns (allowed, retry_after_seconds).
        """
        config = TIER_CONFIGS[tier]
        now = time.time()
        bucket = self._store.get(key)

        if bucket is None or (now - bucket.window_start) >= config.window_seconds:
            self._store[key] = _Bucket(count=1, window_start=now)
            return True, 0

        if bucket.count >= config.requests:
            retry_after = int(config.window_seconds - (now - bucket.window_start)) + 1
            return False, retry_after

        bucket.count += 1
        return True, 0

    def clear(self) -> None:
        """Reset all counters (used in tests)."""
        self._store.clear()
