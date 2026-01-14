"""
Tests for health check endpoints.
"""

import pytest


@pytest.mark.unit
def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "statishub-api"
    assert "version" in data


@pytest.mark.unit
def test_health_check_redis(client, mock_redis):
    """Test Redis health check."""
    response = client.get("/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "redis"
    mock_redis.ping.assert_called_once()


@pytest.mark.unit
def test_health_check_redis_failure(client, mock_redis):
    """Test Redis health check when Redis is down."""
    mock_redis.ping.side_effect = Exception("Connection refused")
    response = client.get("/health/redis")
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.unit
def test_health_check_database(client, mock_supabase):
    """Test database health check."""
    response = client.get("/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "supabase"
