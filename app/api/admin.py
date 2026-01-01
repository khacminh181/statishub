from fastapi import APIRouter, Depends
from app.core.admin_auth import verify_admin
from app.services.api_key import (
    create_api_key,
    revoke_api_key,
    add_credit,
    get_api_key,
    list_api_keys,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin - API Keys"],
    dependencies=[Depends(verify_admin)]
)


@router.post("/api-keys/")
def admin_create_api_key(client_name: str, credits: int = 1000):
    return create_api_key(client_name, credits)


@router.get("/api-keys/")
def admin_list_api_keys(limit: int = 100):
    return list_api_keys(limit)


@router.get("/api-keys/{api_key}")
def admin_get_api_key(api_key: str):
    data = get_api_key(api_key)
    if not data:
        return {"error": "Not found"}
    return data


@router.post("/api-keys/{api_key}/revoke")
def admin_revoke_api_key(api_key: str):
    ok = revoke_api_key(api_key)
    return {"revoked": ok}


@router.post("/api-keys/{api_key}/credit")
def admin_add_credit(api_key: str, amount: int):
    credit = add_credit(api_key, amount)
    if credit is None:
        return {"error": "Not found"}
    return {"credits": credit}
