"""
Rate limiting service using sliding window algorithm.
"""
import time

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.core.redis import redis_client

DEFAULT_RATE_LIMIT = settings.rate_limit_per_minute
WINDOW_SECONDS = 3600


def _config_key(api_key: str) -> str:
    """Generate Redis key for rate limit configuration."""
    return f"apikey_rl:{api_key}"


def set_api_rate_limit(api_key: str, limit_per_hour: int) -> None:
    """Set custom rate limit for an API key."""
    redis_client.set(_config_key(api_key), limit_per_hour)


def get_api_rate_limit(api_key: str) -> int:
    """Get rate limit for an API key, falling back to default."""
    limit = redis_client.get(_config_key(api_key))
    if limit:
        return int(limit)
    return DEFAULT_RATE_LIMIT


def rate_limit_hourly(api_key: str, endpoint: str) -> None:
    """
    Check and enforce hourly rate limit for an API key on a specific endpoint.

    Raises:
        RateLimitExceededError: If rate limit is exceeded
    """
    limit = get_api_rate_limit(api_key)
    now = int(time.time())
    window = now // WINDOW_SECONDS

    redis_key = f"ratelimit:{api_key}:{endpoint}:{window}"
    count = redis_client.incr(redis_key)

    if count == 1:
        redis_client.expire(redis_key, WINDOW_SECONDS)

    if count > limit:
        raise RateLimitExceededError(f"Rate limit exceeded ({limit} req/hour)")
