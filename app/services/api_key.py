"""
API key management service for creating, revoking, and managing API keys.

Uses cryptographically secure key generation for API keys.
"""

import secrets
from datetime import datetime
from typing import Dict, List, Optional

from app.core.redis import redis_client
from app.core.logging import get_logger
from app.services.rate_limit import get_api_rate_limit

logger = get_logger(__name__)

API_KEY_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days


def _generate_secure_api_key() -> str:
    """
    Generate a cryptographically secure API key.

    Uses secrets module for cryptographic randomness instead of uuid.
    Returns a key with 256 bits of entropy (64 hex characters).
    """
    # Use secrets for cryptographically secure random bytes
    random_bytes = secrets.token_hex(32)  # 256 bits of entropy
    return f"sk_{random_bytes}"


def create_api_key(client_name: str, credits: int = 1000) -> Dict:
    """Create a new API key for a client with secure key generation."""
    api_key = _generate_secure_api_key()
    redis_key = f"apikey:{api_key}"

    data = {
        "id": redis_client.incr("apikey:id"),
        "api_key": api_key,
        "client_name": client_name,
        "credits": credits,
        "is_active": 1,
        "created_at": datetime.utcnow().isoformat(),
    }

    redis_client.hset(redis_key, mapping=data)
    redis_client.expire(redis_key, API_KEY_TTL_SECONDS)

    logger.info(f"API key created for client: {client_name}")
    return data


def revoke_api_key(api_key: str) -> bool:
    """Revoke an API key by setting it as inactive."""
    redis_key = f"apikey:{api_key}"
    if not redis_client.exists(redis_key):
        return False

    redis_client.hset(redis_key, "is_active", 0)
    logger.info("API key revoked")
    return True


def get_api_key(api_key: str) -> Optional[Dict]:
    """Get API key details."""
    data = redis_client.hgetall(f"apikey:{api_key}")
    if not data:
        return None
    return data


def list_api_keys(limit: int = 100) -> List[Dict]:
    """List all active API keys with their metadata."""
    keys = redis_client.scan_iter("apikey:sk_*")
    result = []

    for key in keys:
        if len(result) >= limit:
            break

        data = redis_client.hgetall(key)
        if not data:
            continue

        # Skip inactive keys
        if int(data.get("is_active", 0)) != 1:
            continue

        # Convert Redis string values to proper types
        data["credits"] = int(data["credits"])
        data["id"] = int(data["id"])
        data["is_active"] = int(data["is_active"])
        data["rate_limit"] = get_api_rate_limit(data["api_key"])

        result.append(data)

    return result
