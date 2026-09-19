"""Rate Limiting domain layer.

Defines tiers, configuration, and the core contract for rate limiting.
"""
from dataclasses import dataclass
from enum import Enum


class RateLimitTier(Enum):
    AUTH = "auth"
    WRITE = "write"
    READ = "read"
    EXPORT = "export"
    COMPUTE = "compute"
    HEALTH = "health"


@dataclass(frozen=True)
class RateLimitConfig:
    requests: int
    window_seconds: int


TIER_CONFIGS: dict[RateLimitTier, RateLimitConfig] = {
    RateLimitTier.AUTH: RateLimitConfig(requests=5, window_seconds=60),
    RateLimitTier.WRITE: RateLimitConfig(requests=30, window_seconds=60),
    RateLimitTier.READ: RateLimitConfig(requests=100, window_seconds=60),
    RateLimitTier.EXPORT: RateLimitConfig(requests=10, window_seconds=60),
    RateLimitTier.COMPUTE: RateLimitConfig(requests=20, window_seconds=60),
    RateLimitTier.HEALTH: RateLimitConfig(requests=999999, window_seconds=60),
}
