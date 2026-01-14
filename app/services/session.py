"""
Session management service for admin authentication.

Provides secure session tokens instead of storing raw admin keys in cookies.
Sessions are stored in Redis with configurable TTL and signed with HMAC.
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)

SESSION_TTL_SECONDS = 3600  # 1 hour default
SESSION_PREFIX = "admin_session:"


def _generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(32)


def _sign_token(token: str) -> str:
    """
    Create HMAC signature for session token.

    Returns signed token in format: token.signature
    """
    signature = hmac.new(
        settings.admin_key.encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{token}.{signature}"


def _verify_signature(signed_token: str) -> Optional[str]:
    """
    Verify and extract token from signed token.

    Returns the original token if signature is valid, None otherwise.
    Uses timing-safe comparison to prevent timing attacks.
    """
    if not signed_token or "." not in signed_token:
        return None

    try:
        token, signature = signed_token.rsplit(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(
        settings.admin_key.encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Invalid session token signature detected")
        return None

    return token


def create_session(max_age: int = SESSION_TTL_SECONDS) -> str:
    """
    Create a new admin session and return signed token.

    Args:
        max_age: Session TTL in seconds (default 1 hour)

    Returns:
        Signed session token to store in cookie
    """
    token = _generate_session_token()
    session_key = f"{SESSION_PREFIX}{token}"

    session_data = {
        "created_at": str(int(time.time())),
        "expires_at": str(int(time.time()) + max_age),
    }

    redis_client.hset(session_key, mapping=session_data)
    redis_client.expire(session_key, max_age)

    logger.info("Admin session created")
    return _sign_token(token)


def validate_session(signed_token: str) -> bool:
    """
    Validate a session token.

    Verifies both the HMAC signature and Redis session existence.

    Args:
        signed_token: The signed token from cookie

    Returns:
        True if session is valid, False otherwise
    """
    if not signed_token:
        return False

    token = _verify_signature(signed_token)
    if not token:
        return False

    session_key = f"{SESSION_PREFIX}{token}"
    session_data = redis_client.hgetall(session_key)

    if not session_data:
        logger.debug("Session not found in Redis")
        return False

    # Check expiration
    expires_at = int(session_data.get("expires_at", 0))
    if time.time() > expires_at:
        redis_client.delete(session_key)
        logger.debug("Session expired")
        return False

    return True


def invalidate_session(signed_token: str) -> bool:
    """
    Invalidate/logout a session.

    Args:
        signed_token: The signed token from cookie

    Returns:
        True if session was invalidated, False if not found
    """
    if not signed_token:
        return False

    token = _verify_signature(signed_token)
    if not token:
        return False

    session_key = f"{SESSION_PREFIX}{token}"
    deleted = redis_client.delete(session_key) > 0

    if deleted:
        logger.info("Admin session invalidated")

    return deleted
