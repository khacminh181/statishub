"""
Admin authentication for both REST API and web UI.
"""

import hmac

from fastapi import Header, HTTPException, Request

from app.core.config import settings
from app.services.session import validate_session


def verify_admin(x_admin_key: str = Header(...)) -> bool:
    """
    Verify admin API key from request header.

    Uses timing-safe comparison to prevent timing attacks.
    """
    if not hmac.compare_digest(x_admin_key, settings.admin_key):
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


def verify_admin_ui(request: Request) -> bool:
    """
    Verify admin authentication for web UI using session tokens.

    Session tokens are signed with HMAC and stored in Redis.
    This prevents exposing the admin key in cookies.
    """
    if request.url.path.endswith("/login"):
        return True

    session_token = request.cookies.get("session_token")
    if not session_token or not validate_session(session_token):
        raise HTTPException(status_code=403, detail="Forbidden")
    return True
