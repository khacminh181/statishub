"""
CSRF protection for admin UI forms.

Provides token generation and validation to prevent cross-site request forgery attacks.
"""

import secrets

from fastapi import HTTPException, Request, Form

from app.core.redis import redis_client
from app.core.logging import get_logger

logger = get_logger(__name__)

CSRF_TOKEN_TTL = 3600  # 1 hour


def generate_csrf_token(session_token: str) -> str:
    """
    Generate a CSRF token tied to the admin session.

    Args:
        session_token: The admin session token from cookie

    Returns:
        A new CSRF token
    """
    token = secrets.token_urlsafe(32)
    # Use first 16 chars of session token as session ID
    session_id = session_token[:16] if session_token else "anonymous"
    key = f"csrf:{session_id}:{token}"

    redis_client.setex(key, CSRF_TOKEN_TTL, "1")
    logger.debug(f"CSRF token generated for session {session_id[:8]}...")
    return token


def validate_csrf_token(request: Request, csrf_token: str = Form(...)) -> bool:
    """
    Validate a CSRF token from form submission.

    Args:
        request: FastAPI request object
        csrf_token: CSRF token from form

    Returns:
        True if valid

    Raises:
        HTTPException: If token is invalid or missing
    """
    session_token = request.cookies.get("session_token", "")
    session_id = session_token[:16] if session_token else "anonymous"
    key = f"csrf:{session_id}:{csrf_token}"

    if not redis_client.get(key):
        logger.warning(
            "Invalid CSRF token",
            extra={"session_id": session_id[:8] if session_id else "none"},
        )
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Delete token after use (single-use tokens)
    redis_client.delete(key)
    return True


def get_csrf_context(request: Request) -> dict:
    """
    Get template context with CSRF token for rendering forms.

    Args:
        request: FastAPI request object

    Returns:
        Dict with request and csrf_token for template context
    """
    session_token = request.cookies.get("session_token", "")
    csrf_token = generate_csrf_token(session_token)
    return {"request": request, "csrf_token": csrf_token}
