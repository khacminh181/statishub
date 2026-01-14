"""
Redis client initialization for caching and API key storage.

Supports authentication and SSL/TLS for secure connections.
Uses lazy initialization to support testing without running Redis.
"""

import redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level client (lazy initialized)
_redis_client = None


def create_redis_client(skip_ping: bool = False) -> redis.Redis:
    """
    Create Redis client with appropriate security settings.

    Supports:
    - Password authentication via REDIS_PASSWORD
    - SSL/TLS connections via REDIS_SSL

    Args:
        skip_ping: Skip connection test (useful for testing)
    """
    connection_kwargs = {
        "host": settings.redis_host,
        "port": settings.redis_port,
        "db": settings.redis_db,
        "decode_responses": True,
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
    }

    # Add password authentication if configured
    if settings.redis_password:
        connection_kwargs["password"] = settings.redis_password
        logger.info("Redis authentication enabled")

    # Add SSL if configured
    if settings.redis_ssl:
        connection_kwargs["ssl"] = True
        connection_kwargs["ssl_cert_reqs"] = "required"
        logger.info("Redis SSL enabled")

    client = redis.Redis(**connection_kwargs)

    # Test connection on startup (skip in debug/test mode)
    if not skip_ping and not settings.debug:
        try:
            client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    return client


def get_redis_client() -> redis.Redis:
    """Get or create the Redis client (lazy initialization)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = create_redis_client()
    return _redis_client


# For backward compatibility - this is a proxy object
class _RedisClientProxy:
    """Proxy that lazily initializes the Redis client on first use."""

    def __getattr__(self, name):
        return getattr(get_redis_client(), name)


redis_client = _RedisClientProxy()
