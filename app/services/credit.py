"""
Credit consumption management for API keys.

Uses atomic Lua script to prevent race conditions in credit consumption.
"""

from app.core.exceptions import CreditExhaustedError
from app.core.logging import get_logger
from app.core.lua_scripts import consume_credit_script
from app.core.redis import redis_client

logger = get_logger(__name__)


def consume_credit(api_key: str) -> int:
    """
    Atomically consume one credit from the API key.

    Uses Lua script to check balance before decrementing,
    preventing race conditions that could allow overdraft.

    Args:
        api_key: The API key to consume credit from

    Returns:
        New credit balance

    Raises:
        CreditExhaustedError: If no credits remaining
    """
    redis_key = f"apikey:{api_key}"
    result = consume_credit_script.execute(redis_client, 1, redis_key, "credits")

    new_balance, success = result
    if not success:
        logger.warning("Credit exhausted for API key")
        raise CreditExhaustedError()

    logger.debug(f"Credit consumed. Remaining: {new_balance}")
    return new_balance


def add_credit(api_key: str, amount: int) -> int:
    """
    Add credits to an API key.

    Args:
        api_key: The API key to add credits to
        amount: Number of credits to add (can be negative)

    Returns:
        New credit balance, or None if key not found
    """
    redis_key = f"apikey:{api_key}"

    # Check if key exists
    if not redis_client.exists(redis_key):
        return None

    new_balance = redis_client.hincrby(redis_key, "credits", amount)
    logger.info(f"Credits modified. New balance: {new_balance}")
    return new_balance
