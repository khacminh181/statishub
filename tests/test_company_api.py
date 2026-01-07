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
    # Setup cache
    cached_data = {"taxcode": "0123456789", "organizationname": "Cached Company"}
    mock_redis.get.return_value = json.dumps(cached_data)

    response = client.get("/company/0123456789", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["organizationname"] == "Cached Company"


@pytest.mark.integration
def test_get_company_no_cache(client, mock_redis, mock_supabase, api_headers):
    """Test company endpoint without cache."""
    mock_redis.get.return_value = None

    response = client.get("/company/0123456789", headers=api_headers)

    assert response.status_code == 200
    # Should have queried database
    mock_supabase.table.assert_called()
    # Should have cached the result
    mock_redis.setex.assert_called()


@pytest.mark.integration
def test_search_companies(client, mock_redis, mock_supabase, api_headers):
    """Test company search endpoint."""
    mock_redis.get.return_value = None
    mock_supabase.execute.return_value.data = [
        {"taxcode": "0123456789", "organizationname": "Test Company 1"},
        {"taxcode": "9876543210", "organizationname": "Test Company 2"}
    ]

    response = client.get("/search?name=Test", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
