"""
Tests for credit consumption system.

Credit consumption now uses atomic Lua scripts via evalsha.
"""

import pytest
from app.core.exceptions import CreditExhaustedError
from app.core.lua_scripts import consume_credit_script


@pytest.mark.unit
def test_consume_credit_success(mock_redis):
    """Test successful credit consumption with Lua script."""
    from app.services.credit import consume_credit

    # Reset cached script SHA to ensure script_load is called
    consume_credit_script.reset()

    # The mock_redis fixture already sets up smart evalsha handling
    # that returns [99, 1] for credit scripts
    result = consume_credit("test_api_key")

    assert result == 99


@pytest.mark.unit
def test_consume_credit_exhausted(mock_redis):
    """Test credit consumption when credits are exhausted."""
    from app.services.credit import consume_credit

    consume_credit_script.reset()

    # Override evalsha to simulate exhausted credits
    mock_redis.evalsha.side_effect = None
    mock_redis.evalsha.return_value = [0, 0]

    with pytest.raises(CreditExhaustedError):
        consume_credit("test_api_key")


@pytest.mark.unit
def test_consume_credit_exactly_zero(mock_redis):
    """Test credit consumption when exactly 0 credits remain after consumption."""
    from app.services.credit import consume_credit

    consume_credit_script.reset()

    # Override evalsha to simulate zero balance after successful consumption
    mock_redis.evalsha.side_effect = None
    mock_redis.evalsha.return_value = [0, 1]

    # Should succeed with 0 credits remaining after this consumption
    result = consume_credit("test_api_key")
    assert result == 0
