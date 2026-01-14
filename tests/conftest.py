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
os.environ["ADMIN_KEY"] = "TestAdminKey12345678"  # Min 16 chars required
os.environ["ENVIRONMENT"] = "development"  # Skip complexity check in dev
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
    mock.setex.return_value = True
    mock.exists.return_value = False  # For brute force lockout check
    mock.delete.return_value = 1
    mock.hgetall.return_value = {
        "id": "1",
        "api_key": "test_api_key",
        "client_name": "Test Client",
        "credits": "100",
        "is_active": "1",
    }
    mock.hincrby.return_value = 99
    mock.ping.return_value = True
    mock.ttl.return_value = 300

    # Cache storage for test customization
    cache_store = {}

    def mock_get(key):
        """Smart get that returns None for auth keys but cache value for others."""
        if key.startswith("auth_failures:"):
            return None  # No failed attempts
        if key.startswith("company:") or key.startswith("search:"):
            return cache_store.get(key)
        return None

    mock.get.side_effect = mock_get

    # Allow tests to set cache values
    mock._cache_store = cache_store

    # Mock pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = [1, True]
    mock.pipeline.return_value = mock_pipeline

    # Track which script SHA is which
    script_shas = {"rate_limit": "rate_sha", "credit": "credit_sha", "ip_rate": "ip_sha"}
    call_count = [0]

    def mock_script_load(script):
        call_count[0] += 1
        if "HGET" in script:  # Credit script uses HGET
            return script_shas["credit"]
        elif "ZCARD" in script:  # Rate limit uses sorted sets
            return script_shas["rate_limit"]
        return f"sha_{call_count[0]}"

    def mock_evalsha(sha, num_keys, *args):
        if sha == script_shas["credit"]:
            return [99, 1]  # Credit: [new_balance, success]
        else:
            return [1, 1, 0]  # Rate limit: [count, allowed, retry_after]

    mock.script_load.side_effect = mock_script_load
    mock.evalsha.side_effect = mock_evalsha

    from app.core import redis
    from app.core.lua_scripts import sliding_window_script, consume_credit_script

    # Reset cached Lua script SHAs to ensure they use the mock
    sliding_window_script.reset()
    consume_credit_script.reset()

    # Patch the internal _redis_client that the proxy uses
    monkeypatch.setattr(redis, "_redis_client", mock)
    return mock


@pytest.fixture
def mock_request():
    """Mock FastAPI request for testing auth functions."""
    mock = MagicMock()
    mock.client.host = "127.0.0.1"
    mock.headers = {}
    return mock


@pytest.fixture
def mock_supabase(monkeypatch):
    """Mock Supabase client for testing."""
    mock = MagicMock()

    # Track if single() was called to return appropriate response
    mock._single_called = False

    # Mock response structures
    list_response = MagicMock()
    list_response.data = [
        {
            "taxcode": "0123456789",
            "organizationid": 1,
            "organizationname": "Test Company",
            "ishistory": False,
        }
    ]
    list_response.count = 1

    single_response = MagicMock()
    single_response.data = {
        "taxcode": "0123456789",
        "organizationid": 1,
        "organizationname": "Test Company",
        "ishistory": False,
    }

    def mark_single():
        mock._single_called = True
        return mock

    def get_execute():
        if mock._single_called:
            mock._single_called = False  # Reset for next chain
            return single_response
        return list_response

    # Setup fluent API chain
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.single.side_effect = mark_single
    mock.execute.side_effect = get_execute
    mock.limit.return_value = mock
    mock.in_.return_value = mock
    mock.or_.return_value = mock
    mock.ilike.return_value = mock
    mock.order.return_value = mock
    mock.range.return_value = mock

    # Patch at the database module
    from app import database

    monkeypatch.setattr(database, "supabase", mock)

    # Also patch at the actual import locations (where "from app.database import supabase" is used)
    from app.api import company, health

    monkeypatch.setattr(company, "supabase", mock)
    monkeypatch.setattr(health, "supabase", mock)

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
