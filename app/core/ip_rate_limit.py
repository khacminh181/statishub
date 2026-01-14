"""
IP-based rate limiting for public endpoints.

Provides rate limiting based on client IP address for endpoints
that don't require API key authentication (like health checks).
"""

import time
import uuid

from fastapi import Request

from app.core.client_ip import get_client_ip, hash_ip
from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger
from app.core.lua_scripts import sliding_window_script
from app.core.redis import redis_client

logger = get_logger(__name__)

IP_RATE_LIMIT = 30  # requests per minute
IP_WINDOW_SECONDS = 60  # 1 minute window


def ip_rate_limit_dep(request: Request) -> None:
    """
    FastAPI dependency for IP-based rate limiting on public endpoints.

    Applies a stricter rate limit (30 req/min) to prevent abuse
    of unauthenticated endpoints.

    Args:
        request: FastAPI request object

    Raises:
        RateLimitExceededError: If rate limit exceeded
    """
    client_ip = get_client_ip(request)
    ip_hash = hash_ip(client_ip, length=12)

    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path

    redis_key = f"ip_rl:{ip_hash}:{endpoint}"
    now = time.time()
    request_id = f"{now}:{uuid.uuid4().hex[:8]}"

    try:
        result = sliding_window_script.execute(
            redis_client, 1, redis_key, IP_RATE_LIMIT, IP_WINDOW_SECONDS, now, request_id
        )

        current_count, is_allowed, retry_after = result

        if not is_allowed:
            logger.warning(
                "IP rate limit exceeded",
                extra={
                    "ip_hash": ip_hash,
                    "endpoint": endpoint,
                    "count": current_count,
                    "retry_after": retry_after,
                },
            )
            raise RateLimitExceededError(f"Too many requests. Retry after {retry_after} seconds.")

    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.error(f"IP rate limit check failed: {e}")
