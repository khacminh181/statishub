"""
Credit consumption management for API keys.
"""
from app.core.redis import redis_client
from app.core.exceptions import CreditExhaustedError
from app.core.logging import get_logger

logger = get_logger(__name__)


def consume_credit(api_key: str):
    """
    Consume one credit from the API key.

    Args:
        api_key: The API key to consume credit from

    Raises:
        CreditExhaustedError: If no credits remaining
    """
    redis_key = f"apikey:{api_key}"
    credit = redis_client.hincrby(redis_key, "credits", -1)

    if credit < 0:
        logger.warning(f"Credit exhausted for API key: {api_key[:8]}...")
        # Restore the credit since we're rejecting the request
        redis_client.hincrby(redis_key, "credits", 1)
        raise CreditExhaustedError()

    logger.debug(f"Credit consumed. Remaining: {credit}")