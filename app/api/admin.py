"""
Admin API endpoints for managing API keys and rate limits.
"""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends

from app.core.admin_auth import verify_admin
from app.services.api_key import (
    add_credit,
    create_api_key,
    get_api_key,
    list_api_keys,
    revoke_api_key,
)
from app.services.rate_limit import set_api_rate_limit

router = APIRouter(
    prefix="/admin",
    tags=["Admin - API Keys"],
    dependencies=[Depends(verify_admin)],
)


@router.post("/api-keys/")
def admin_create_api_key(client_name: str, credits: int = 1000) -> Dict:
    """Create a new API key for a client."""
    return create_api_key(client_name, credits)


@router.get("/api-keys/")
def admin_list_api_keys(limit: int = 100) -> List[Dict]:
    """List all active API keys."""
    return list_api_keys(limit)


@router.get("/api-keys/{api_key}")
def admin_get_api_key(api_key: str) -> Dict:
    """Get details of a specific API key."""
    data = get_api_key(api_key)
    if not data:
        return {"error": "Not found"}
    return data


@router.post("/api-keys/{api_key}/revoke")
def admin_revoke_api_key(api_key: str) -> Dict[str, bool]:
    """Revoke an API key."""
    ok = revoke_api_key(api_key)
    return {"revoked": ok}


@router.post("/api-keys/{api_key}/credit")
def admin_add_credit(api_key: str, amount: int) -> Dict:
    """Add credits to an API key."""
    credit = add_credit(api_key, amount)
    if credit is None:
        return {"error": "Not found"}
    return {"credits": credit}


@router.post("/api-keys/{api_key}/rate-limit")
def admin_set_rate_limit(api_key: str, limit_per_hour: int) -> Dict[str, bool]:
    """Set rate limit for an API key."""
    set_api_rate_limit(api_key, limit_per_hour)
    return {"ok": True}
