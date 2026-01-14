"""
Integration tests for company API endpoints.
"""

import pytest
import json


@pytest.mark.integration
def test_get_company_unauthorized(client):
    """Test company endpoint without API key."""
    response = client.get("/company/0123456789")
    assert response.status_code in [401, 422]  # 422 if missing header


@pytest.mark.integration
def test_get_company_with_cache(client, mock_redis, mock_supabase, api_headers):
    """Test company endpoint with cached data."""
    # Setup cache using the internal cache store
    cached_data = {"taxcode": "0123456789", "organizationname": "Cached Company"}
    mock_redis._cache_store["company:0123456789:en"] = json.dumps(cached_data)

    response = client.get("/company/0123456789", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["organizationname"] == "Cached Company"


@pytest.mark.integration
def test_get_company_no_cache(client, mock_redis, mock_supabase, api_headers):
    """Test company endpoint without cache (cache miss)."""
    # Cache store is empty by default - no need to set anything

    response = client.get("/company/0123456789", headers=api_headers)

    assert response.status_code == 200
    # Should have queried database
    mock_supabase.table.assert_called()
    # Should have cached the result
    mock_redis.setex.assert_called()


@pytest.mark.integration
def test_search_companies(client, mock_redis, mock_supabase, api_headers):
    """Test company search endpoint."""
    # Cache store is empty by default - will hit the database
    # The mock_supabase fixture returns a default list with 1 item

    response = client.get("/search?name=Test", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert "data" in data  # The actual response key is 'data', not 'results'
    assert "pagination" in data
    # Default mock returns 1 item
    assert len(data["data"]) >= 1
    assert "organizationname" in data["data"][0]
