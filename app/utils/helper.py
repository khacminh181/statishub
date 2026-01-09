"""
Utility helper functions.
"""
import json
from typing import Any, List, Optional

from app.core.redis import redis_client

CACHE_TTL_SECONDS = 3600


def build_search_cache_key(name: str, limit: int, offset: int) -> str:
    """Build cache key for organization search."""
    return f"search:organization:{name.lower()}:{limit}:{offset}"


def build_cache_key(prefix: str, taxcode: str, language: str) -> str:
    """Build cache key for company data endpoints."""
    return f"{prefix}:{taxcode}:{language}"


def get_cached(cache_key: str) -> Optional[Any]:
    """Get cached data from Redis."""
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None


def set_cached(cache_key: str, data: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
    """Store data in Redis cache."""
    redis_client.setex(cache_key, ttl, json.dumps(data, default=str))


def inject_taxcode(rows: List, taxcode: str) -> List:
    """Inject taxcode into each row of results."""
    for row in rows:
        row["taxcode"] = taxcode
    return rows
