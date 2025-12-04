# tests/test_endpoints/test_health.py
"""
Tests for health check endpoints.
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test suite for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "environment" in data
    
    def test_liveness_check(self, client):
        """Test liveness probe endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"
    
    def test_readiness_check(self, client):
        """Test readiness probe endpoint."""
        response = client.get("/health/ready")
        
        # May be 200 or 503 depending on if Gemini client is initialized
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "uptime_seconds" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "uptime_seconds" in data
        assert "environment" in data
        assert "gemini_available" in data
        assert "version" in data
