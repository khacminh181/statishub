"""
API key authentication and verification with brute force protection.
"""

from typing import Dict

from fastapi import Header, Request

from app.core.client_ip import get_client_ip, hash_ip
from app.core.exceptions import APIKeyInvalidError, BruteForceProtectionError
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 300  # 5 minutes


def _check_brute_force(client_ip: str) -> None:
    """
    Check if client IP is locked out due to too many failed attempts.

    Raises:
        BruteForceProtectionError: If locked out
    """
    ip_hash = hash_ip(client_ip)
    key = f"auth_failures:{ip_hash}"
    attempts = redis_client.get(key)

    if attempts and int(attempts) >= MAX_FAILED_ATTEMPTS:
        ttl = redis_client.ttl(key)
        logger.warning(
            "Brute force protection triggered",
            extra={"ip_hash": ip_hash, "attempts": attempts, "ttl": ttl},
        )
        raise BruteForceProtectionError(f"Too many failed attempts. Try again in {ttl} seconds.")


def _record_failed_attempt(client_ip: str) -> None:
    """Record a failed authentication attempt."""
    ip_hash = hash_ip(client_ip)
    key = f"auth_failures:{ip_hash}"

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, LOCKOUT_WINDOW_SECONDS)
    pipe.execute()

    logger.warning(
        "Failed authentication attempt recorded",
        extra={"ip_hash": ip_hash},
    )


def _clear_failed_attempts(client_ip: str) -> None:
    """Clear failed attempts counter on successful authentication."""
    ip_hash = hash_ip(client_ip)
    key = f"auth_failures:{ip_hash}"
    redis_client.delete(key)


def verify_api_key(request: Request, x_api_key: str = Header(...)) -> Dict:
    """
    Verify API key from Redis and return client information.

    Includes brute force protection - blocks IPs after too many failed attempts.

    Args:
        request: FastAPI request object for IP extraction
        x_api_key: API key from request header

    Returns:
        Client information including id, api_key, client_name, credits

    Raises:
        APIKeyInvalidError: If API key is invalid or inactive
        BruteForceProtectionError: If too many failed attempts from IP
    """
    client_ip = get_client_ip(request)

    # Check brute force protection before attempting validation
    _check_brute_force(client_ip)

    redis_key = f"apikey:{x_api_key}"
    data = redis_client.hgetall(redis_key)

    if not data or data.get("is_active") != "1":
        _record_failed_attempt(client_ip)
        logger.warning(
            "Invalid API key attempt",
            extra={"ip_hash": hash_ip(client_ip)},
        )
        raise APIKeyInvalidError()

    # Clear failed attempts on successful auth
    _clear_failed_attempts(client_ip)

    logger.debug(f"API key verified for client: {data.get('client_name')}")

    return {
        "id": int(data["id"]),
        "api_key": x_api_key,
        "client_name": data["client_name"],
        "credits": int(data["credits"]),
    }
