from fastapi import APIRouter, Request, Depends, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.admin_auth import verify_admin_ui
from app.services.api_key import (
    create_api_key,
    revoke_api_key,
    add_credit,
    list_api_keys,
)
from app.core.config import settings

router = APIRouter(
    prefix="/admin-ui",
    include_in_schema=False,
    dependencies=[Depends(verify_admin_ui)]
)

templates = Jinja2Templates(directory="app/adminui/templates")

# @router.post("/login")
# def admin_login(response: Response, key: str = Form(...)):
#     if key != admin_key:
#         raise HTTPException(status_code=403)

#     response.set_cookie("admin_key", key, httponly=True)
#     return RedirectResponse("/admin-ui/api-keys", status_code=303)

@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@router.post("/login")
def admin_login(response: Response, key: str = Form(...)):
    if key != settings.admin_key:
        raise HTTPException(status_code=403)

    response = RedirectResponse("/admin-ui/api-keys", status_code=303)
    response.set_cookie(
        "admin_key",
        key,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response

@router.get("/api-keys", response_class=HTMLResponse)
def ui_list_api_keys(request: Request):
    items = list_api_keys(limit=100)
    return templates.TemplateResponse(
        "api_keys.html",
        {
            "request": request,
            "items": items
        }
    )


@router.post("/api-keys/create")
def ui_create_api_key(
    client_name: str = Form(...),
    credits: int = Form(1000)
):
    create_api_key(client_name, credits)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/revoke")
def ui_revoke_api_key(api_key: str):
    revoke_api_key(api_key)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)


@router.post("/api-keys/{api_key}/credit")
def ui_add_credit(
    api_key: str,
    amount: int = Form(...)
):
    add_credit(api_key, amount)
    return RedirectResponse("/admin-ui/api-keys", status_code=303)
