# app/core/rate_limit.py

from fastapi import Request,Depends
from app.core.auth import verify_api_key
from app.services.rate_limit import rate_limit_hourly

def rate_limit_dep(
    request: Request,
    api_key=Depends(verify_api_key),
):
    # endpoint = request.url.path
    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path
    rate_limit_hourly(api_key["api_key"], endpoint)