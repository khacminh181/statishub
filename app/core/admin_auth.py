"""
Admin authentication for both REST API and web UI.
"""
from fastapi import Header, HTTPException, Request
from app.core.config import settings


def verify_admin(x_admin_key: str = Header(...)):
    """Verify admin API key from request header."""
    if x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


def verify_admin_ui(request: Request):
    """Verify admin authentication for web UI using cookies."""
    if request.url.path.endswith("/login"):
        return True

    token = request.cookies.get("admin_key")
    if token != settings.admin_key:
        raise HTTPException(status_code=403)
