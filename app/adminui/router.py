"""
Admin web UI routes for managing API keys.
"""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.admin_auth import verify_admin_ui
from app.core.config import settings
from app.services.api_key import add_credit, create_api_key, list_api_keys, revoke_api_key
from app.services.rate_limit import set_api_rate_limit

router = APIRouter(
    prefix="/admin-ui",
    include_in_schema=False,
    dependencies=[Depends(verify_admin_ui)],
)

templates = Jinja2Templates(directory="app/adminui/templates")


@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request) -> HTMLResponse:
    """Render admin login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def admin_login(key: str = Form(...)) -> RedirectResponse:
    """Handle admin login form submission."""
    if key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    response = RedirectResponse("/admin-ui/api-keys", status_code=303)
    response.set_cookie(
        "admin_key",
        key,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    return response


@router.get("/api-keys", response_class=HTMLResponse)
def ui_list_api_keys(request: Request) -> HTMLResponse:
    """List all API keys in admin UI."""
    items = list_api_keys(limit=100)
    return templates.TemplateResponse("api_keys.html", {"request": request, "items": items})


@router.post("/api-keys/create")
def ui_create_api_key(
    client_name: str = Form(...),
    credits: int = Form(1000),
) -> RedirectResponse:
    """Create a new API key from admin UI."""
    create_api_key(client_name, credits)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/revoke")
def ui_revoke_api_key(api_key: str) -> RedirectResponse:
    """Revoke an API key from admin UI."""
    revoke_api_key(api_key)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/credit")
def ui_add_credit(api_key: str, amount: int = Form(...)) -> RedirectResponse:
    """Add credits to an API key from admin UI."""
    add_credit(api_key, amount)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/rate-limit")
def ui_set_rate_limit(api_key: str, limit: int = Form(...)) -> RedirectResponse:
    """Set rate limit for an API key from admin UI."""
    set_api_rate_limit(api_key, limit)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)

