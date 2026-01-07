"""
Tests for authentication and authorization.
"""
import pytest
from app.core.exceptions import APIKeyInvalidError


@pytest.mark.unit
def test_verify_api_key_valid(mock_redis):
    """Test API key verification with valid key."""
    from app.core.auth import verify_api_key

    result = verify_api_key(x_api_key="test_api_key")

    assert result["api_key"] == "test_api_key"
    assert result["client_name"] == "Test Client"
    assert result["credits"] == 100
    mock_redis.hgetall.assert_called_with("apikey:test_api_key")


@pytest.mark.unit
def test_verify_api_key_invalid(mock_redis):
    """Test API key verification with invalid key."""
    from app.core.auth import verify_api_key

    mock_redis.hgetall.return_value = {}

    with pytest.raises(APIKeyInvalidError):
        verify_api_key(x_api_key="invalid_key")


@pytest.mark.unit
def test_verify_api_key_inactive(mock_redis):
    """Test API key verification with inactive key."""
    from app.core.auth import verify_api_key

    mock_redis.hgetall.return_value = {
        "id": "1",
        "is_active": "0"  # Inactive
    }

    with pytest.raises(APIKeyInvalidError):
        verify_api_key(x_api_key="inactive_key")
