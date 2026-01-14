"""
Rate limiting for admin authentication attempts.

Provides protection against brute force attacks on the admin login.
"""

from app.core.client_ip import hash_ip
from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)

ADMIN_LOGIN_MAX_ATTEMPTS = 5
ADMIN_LOGIN_WINDOW_SECONDS = 300  # 5 minutes
ADMIN_LOGIN_LOCKOUT_SECONDS = 900  # 15 minutes lockout after max attempts


def check_admin_login_rate_limit(client_ip: str) -> None:
    """
    Check if client IP is rate limited for admin login.

    Args:
        client_ip: The client's IP address

    Raises:
        RateLimitExceededError: If rate limit exceeded or locked out
    """
    ip_hash = hash_ip(client_ip)
    lockout_key = f"admin_lockout:{ip_hash}"

    # Check if currently locked out
    if redis_client.exists(lockout_key):
        ttl = redis_client.ttl(lockout_key)
        logger.warning(
            "Admin login locked out",
            extra={"ip_hash": ip_hash, "ttl": ttl},
        )
        raise RateLimitExceededError(f"Too many login attempts. Try again in {ttl} seconds.")

    # Check recent attempts
    attempts_key = f"admin_attempts:{ip_hash}"
    attempts = redis_client.get(attempts_key)

    if attempts and int(attempts) >= ADMIN_LOGIN_MAX_ATTEMPTS:
        # Set lockout
        redis_client.setex(lockout_key, ADMIN_LOGIN_LOCKOUT_SECONDS, "1")
        redis_client.delete(attempts_key)
        logger.warning(
            "Admin login lockout triggered",
            extra={"ip_hash": ip_hash, "lockout_seconds": ADMIN_LOGIN_LOCKOUT_SECONDS},
        )
        raise RateLimitExceededError(
            f"Too many login attempts. Locked out for {ADMIN_LOGIN_LOCKOUT_SECONDS} seconds."
        )


def record_admin_login_attempt(client_ip: str, success: bool) -> None:
    """
    Record an admin login attempt.

    Args:
        client_ip: The client's IP address
        success: Whether the login attempt was successful
    """
    ip_hash = hash_ip(client_ip)
    attempts_key = f"admin_attempts:{ip_hash}"

    if success:
        # Clear attempts on successful login
        redis_client.delete(attempts_key)
        logger.info("Admin login successful", extra={"ip_hash": ip_hash})
    else:
        # Increment failed attempts
        pipe = redis_client.pipeline()
        pipe.incr(attempts_key)
        pipe.expire(attempts_key, ADMIN_LOGIN_WINDOW_SECONDS)
        pipe.execute()
        logger.warning(
            "Admin login failed",
            extra={"ip_hash": ip_hash},
        )
