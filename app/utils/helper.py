"""
Utility helper functions.
"""

import hashlib
import json
import re
from typing import Any, List, Optional

from app.core.redis import redis_client

CACHE_TTL_SECONDS = 3600


def _sanitize_cache_component(value: str) -> str:
    """
    Sanitize a cache key component to prevent cache key injection.

    Only allows alphanumeric characters, underscores, and hyphens.
    """
    return re.sub(r"[^a-zA-Z0-9_\-]", "", str(value))


def build_search_cache_key(name: str, limit: int, offset: int) -> str:
    """
    Build cache key for organization search.

    Uses hash of search term to avoid cache key injection.
    """
    # Hash the name to prevent cache key manipulation
    name_hash = hashlib.sha256(name.lower().encode()).hexdigest()[:16]
    return f"search:organization:{name_hash}:{limit}:{offset}"


def build_cache_key(prefix: str, taxcode: str, language: str) -> str:
    """Build cache key for company data endpoints with sanitization."""
    safe_prefix = _sanitize_cache_component(prefix)
    safe_taxcode = _sanitize_cache_component(taxcode)
    safe_language = _sanitize_cache_component(language)
    return f"{safe_prefix}:{safe_taxcode}:{safe_language}"


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
