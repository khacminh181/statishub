"""
Admin web UI routes for managing API keys.
"""

import hmac

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.admin_auth import verify_admin_ui
from app.core.client_ip import get_client_ip
from app.core.config import settings
from app.core.csrf import get_csrf_context, validate_csrf_token
from app.services.admin_rate_limit import check_admin_login_rate_limit, record_admin_login_attempt
from app.services.api_key import create_api_key, list_api_keys, revoke_api_key
from app.services.credit import add_credit
from app.services.rate_limit import set_api_rate_limit
from app.services.session import create_session, invalidate_session

router = APIRouter(
    prefix="/admin-ui",
    include_in_schema=False,
    dependencies=[Depends(verify_admin_ui)],
)

templates = Jinja2Templates(directory="app/adminui/templates")

SESSION_MAX_AGE = 3600  # 1 hour


@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request) -> HTMLResponse:
    """Render admin login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def admin_login(request: Request, key: str = Form(...)) -> RedirectResponse:
    """Handle admin login form submission with session-based auth and rate limiting."""
    client_ip = get_client_ip(request)

    # Check rate limit before processing login
    check_admin_login_rate_limit(client_ip)

    # Use timing-safe comparison to prevent timing attacks
    if not hmac.compare_digest(key, settings.admin_key):
        record_admin_login_attempt(client_ip, success=False)
        raise HTTPException(status_code=403, detail="Invalid admin key")

    # Record successful login
    record_admin_login_attempt(client_ip, success=True)

    # Create secure session token instead of storing admin key
    session_token = create_session(max_age=SESSION_MAX_AGE)

    response = RedirectResponse("/admin-ui/api-keys", status_code=303)
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )
    return response


@router.post("/logout")
def admin_logout(request: Request) -> RedirectResponse:
    """Handle admin logout - invalidate session."""
    session_token = request.cookies.get("session_token")
    if session_token:
        invalidate_session(session_token)

    response = RedirectResponse("/admin-ui/login", status_code=303)
    response.delete_cookie("session_token")
    return response


@router.get("/api-keys", response_class=HTMLResponse)
def ui_list_api_keys(request: Request) -> HTMLResponse:
    """List all API keys in admin UI with CSRF token for forms."""
    items = list_api_keys(limit=100)
    context = get_csrf_context(request)
    context["items"] = items
    return templates.TemplateResponse("api_keys.html", context)


@router.post("/api-keys/create")
def ui_create_api_key(
    request: Request,
    client_name: str = Form(...),
    credits: int = Form(1000),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """Create a new API key from admin UI with CSRF protection."""
    validate_csrf_token(request, csrf_token)
    create_api_key(client_name, credits)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/revoke")
def ui_revoke_api_key(
    request: Request,
    api_key: str,
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """Revoke an API key from admin UI with CSRF protection."""
    validate_csrf_token(request, csrf_token)
    revoke_api_key(api_key)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/credit")
def ui_add_credit(
    request: Request,
    api_key: str,
    amount: int = Form(...),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """Add credits to an API key from admin UI with CSRF protection."""
    validate_csrf_token(request, csrf_token)
    add_credit(api_key, amount)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/rate-limit")
def ui_set_rate_limit(
    request: Request,
    api_key: str,
    limit: int = Form(...),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """Set rate limit for an API key from admin UI with CSRF protection."""
    validate_csrf_token(request, csrf_token)
    set_api_rate_limit(api_key, limit)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)
