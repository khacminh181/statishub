"""
Admin API endpoints for managing API keys and rate limits.

All endpoints require admin authentication via x-admin-key header.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.core.admin_auth import verify_admin
from app.services.api_key import (
    create_api_key,
    get_api_key,
    list_api_keys,
    revoke_api_key,
)
from app.services.credit import add_credit
from app.services.rate_limit import set_api_rate_limit

router = APIRouter(
    prefix="/admin",
    tags=["Admin - API Keys"],
    dependencies=[Depends(verify_admin)],
)


# Request validation models
class CreateApiKeyRequest(BaseModel):
    """Request model for creating API keys."""

    client_name: str = Field(..., min_length=1, max_length=100, description="Client name")
    credits: int = Field(default=1000, ge=0, le=10000000, description="Initial credits")


class AddCreditRequest(BaseModel):
    """Request model for adding credits."""

    amount: int = Field(..., ge=-1000000, le=1000000, description="Credit amount (can be negative)")

    @field_validator("amount")
    @classmethod
    def amount_not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v


class SetRateLimitRequest(BaseModel):
    """Request model for setting rate limits."""

    limit_per_hour: int = Field(..., ge=1, le=100000, description="Rate limit per hour")


@router.post("/api-keys/")
def admin_create_api_key(request: CreateApiKeyRequest) -> Dict:
    """Create a new API key for a client with validated input."""
    return create_api_key(request.client_name, request.credits)


@router.get("/api-keys/")
def admin_list_api_keys(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum keys to return")
) -> List[Dict]:
    """List all active API keys."""
    return list_api_keys(limit)


@router.get("/api-keys/{api_key}")
def admin_get_api_key(api_key: str) -> Dict:
    """Get details of a specific API key."""
    data = get_api_key(api_key)
    if not data:
        raise HTTPException(status_code=404, detail="API key not found")
    return data


@router.post("/api-keys/{api_key}/revoke")
def admin_revoke_api_key(api_key: str) -> Dict[str, bool]:
    """Revoke an API key."""
    # Verify key exists first
    if not get_api_key(api_key):
        raise HTTPException(status_code=404, detail="API key not found")
    ok = revoke_api_key(api_key)
    return {"revoked": ok}


@router.post("/api-keys/{api_key}/credit")
def admin_add_credit(api_key: str, request: AddCreditRequest) -> Dict:
    """Add credits to an API key with validated input."""
    # Verify key exists first
    if not get_api_key(api_key):
        raise HTTPException(status_code=404, detail="API key not found")
    credit = add_credit(api_key, request.amount)
    if credit is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"credits": credit}


@router.post("/api-keys/{api_key}/rate-limit")
def admin_set_rate_limit(api_key: str, request: SetRateLimitRequest) -> Dict[str, bool]:
    """Set rate limit for an API key with validated input."""
    # Verify key exists first
    if not get_api_key(api_key):
        raise HTTPException(status_code=404, detail="API key not found")
    set_api_rate_limit(api_key, request.limit_per_hour)
    return {"ok": True, "limit_per_hour": request.limit_per_hour}
