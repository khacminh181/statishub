"""
Client IP extraction and hashing utilities.

Provides consistent handling of client IP addresses across the application,
including proxy header support and privacy-preserving hashing.
"""

import hashlib
from typing import Optional

from fastapi import Request


def get_client_ip(request: Optional[Request]) -> str:
    """
    Extract client IP from request, handling proxy headers.

    Checks X-Forwarded-For and X-Real-IP headers for load balancer/proxy scenarios.
    Returns the original client IP when behind proxies.

    Args:
        request: FastAPI request object, or None

    Returns:
        Client IP address string, or "unknown" if unavailable
    """
    if request is None:
        return "unknown"

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def hash_ip(ip: str, length: int = 16) -> str:
    """
    Hash IP address for privacy in Redis keys and logs.

    Args:
        ip: IP address to hash
        length: Length of hash to return (default 16)

    Returns:
        Truncated SHA-256 hash of IP address
    """
    return hashlib.sha256(ip.encode()).hexdigest()[:length]
