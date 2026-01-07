"""
Pytest configuration and fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import os

# Set test environment variables before importing app
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test_key"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_DB"] = "1"  # Use different DB for testing
os.environ["ADMIN_KEY"] = "test_admin_key"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client for testing."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.hgetall.return_value = {
        "id": "1",
        "api_key": "test_api_key",
        "client_name": "Test Client",
        "credits": "100",
        "is_active": "1"
    }
    mock.hincrby.return_value = 99
    mock.ping.return_value = True

    from app.core import redis
    monkeypatch.setattr(redis, "redis_client", mock)
    return mock


@pytest.fixture
def mock_supabase(monkeypatch):
    """Mock Supabase client for testing."""
    mock = MagicMock()

    # Mock response structure
    mock_response = MagicMock()
    mock_response.data = [{
        "taxcode": "0123456789",
        "organizationid": 1,
        "organizationname": "Test Company",
        "ishistory": False
    }]

    # Setup fluent API chain
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.single.return_value = mock
    mock.execute.return_value = mock_response
    mock.limit.return_value = mock
    mock.in_.return_value = mock

    from app import database
    monkeypatch.setattr(database, "supabase", mock)
    return mock


@pytest.fixture
def valid_api_key():
    """Valid API key for testing."""
    return "test_api_key"


@pytest.fixture
def api_headers(valid_api_key):
    """HTTP headers with valid API key."""
    return {"x-api-key": valid_api_key}


@pytest.fixture
def admin_headers():
    """HTTP headers with valid admin key."""
    return {"x-admin-key": "test_admin_key"}
