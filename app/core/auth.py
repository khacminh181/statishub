# app/core/auth.py
from fastapi import Header, HTTPException, Depends

VALID_API_KEYS = {"demo-key-123"}

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
