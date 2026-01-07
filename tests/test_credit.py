"""
Tests for credit consumption system.
"""
import pytest
from app.core.exceptions import CreditExhaustedError


@pytest.mark.unit
def test_consume_credit_success(mock_redis):
    """Test successful credit consumption."""
    from app.services.credit import consume_credit

    mock_redis.hincrby.return_value = 99

    consume_credit("test_api_key")

    mock_redis.hincrby.assert_called_once_with("apikey:test_api_key", "credits", -1)


@pytest.mark.unit
def test_consume_credit_exhausted(mock_redis):
    """Test credit consumption when credits are exhausted."""
    from app.services.credit import consume_credit

    mock_redis.hincrby.return_value = -1

    with pytest.raises(CreditExhaustedError):
        consume_credit("test_api_key")

    # Should restore the credit
    assert mock_redis.hincrby.call_count == 2


@pytest.mark.unit
def test_consume_credit_exactly_zero(mock_redis):
    """Test credit consumption when exactly 0 credits remain."""
    from app.services.credit import consume_credit

    mock_redis.hincrby.return_value = 0

    # Should succeed with 0 credits remaining
    consume_credit("test_api_key")
