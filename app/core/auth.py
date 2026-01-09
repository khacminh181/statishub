"""
API key authentication and verification.
"""
from typing import Dict

from fastapi import Header

from app.core.exceptions import APIKeyInvalidError
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)


def verify_api_key(x_api_key: str = Header(...)) -> Dict:
    """
    Verify API key from Redis and return client information.

    Args:
        x_api_key: API key from request header

    Returns:
        Client information including id, api_key, client_name, credits

    Raises:
        APIKeyInvalidError: If API key is invalid or inactive
    """
    redis_key = f"apikey:{x_api_key}"
    data = redis_client.hgetall(redis_key)

    if not data or data.get("is_active") != "1":
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise APIKeyInvalidError()

    logger.debug(f"API key verified for client: {data.get('client_name')}")

    return {
        "id": int(data["id"]),
        "api_key": x_api_key,
        "client_name": data["client_name"],
        "credits": int(data["credits"]),
    }