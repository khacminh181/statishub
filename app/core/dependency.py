"""
FastAPI dependency functions for request handling.
"""
from typing import Dict

from fastapi import Depends, Request

from app.core.auth import verify_api_key
from app.services.rate_limit import rate_limit_hourly


def rate_limit_dep(
    request: Request,
    api_key: Dict = Depends(verify_api_key),
) -> None:
    """
    Dependency to enforce rate limiting on API endpoints.

    Uses the route path pattern (not the actual URL path) for consistent
    rate limiting across parameterized endpoints.
    """
    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path
    rate_limit_hourly(api_key["api_key"], endpoint)