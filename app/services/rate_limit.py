"""
Rate limiting service using atomic sliding window algorithm.

Uses Redis Lua scripts to ensure thread-safe rate limiting without race conditions.
"""

import time
import uuid

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger
from app.core.lua_scripts import sliding_window_script
from app.core.redis import redis_client

logger = get_logger(__name__)

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
    return int(limit) if limit else DEFAULT_RATE_LIMIT


def rate_limit_hourly(api_key: str, endpoint: str) -> tuple:
    """
    Check and enforce hourly rate limit using atomic sliding window.

    Uses Lua script to atomically check and increment rate limit counter,
    preventing race conditions that could allow rate limit bypass.

    Args:
        api_key: The API key to rate limit
        endpoint: The endpoint being accessed

    Returns:
        Tuple of (current_count, retry_after_seconds)

    Raises:
        RateLimitExceededError: If rate limit is exceeded
    """
    limit = get_api_rate_limit(api_key)
    now = time.time()
    request_id = f"{now}:{uuid.uuid4().hex[:8]}"
    redis_key = f"ratelimit:sw:{api_key}:{endpoint}"

    result = sliding_window_script.execute(
        redis_client, 1, redis_key, limit, WINDOW_SECONDS, now, request_id
    )

    current_count, is_allowed, retry_after = result

    if not is_allowed:
        logger.warning(
            "Rate limit exceeded",
            extra={
                "endpoint": endpoint,
                "count": current_count,
                "limit": limit,
                "retry_after": retry_after,
            },
        )
        raise RateLimitExceededError(
            f"Rate limit exceeded ({limit} req/hour). Retry after {retry_after} seconds."
        )

    return current_count, retry_after
