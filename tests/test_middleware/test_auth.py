# tests/test_middleware/test_auth.py
"""
Tests for API key authentication middleware.
"""
import pytest
import os
from fastapi import status


class TestAPIKeyAuth:
    """Test suite for API key authentication."""
    
    def test_public_endpoints_no_auth_required(self, client):
        """Test that public endpoints don't require authentication."""
        public_endpoints = ["/", "/health", "/health/live", "/health/ready", "/docs"]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            # Should not get 401 Unauthorized
            assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_without_api_key(self, client):
        """Test that protected endpoints require API key when auth is enabled."""
        # Enable auth for this test
        os.environ["API_AUTH_ENABLED"] = "true"
        
        # Reload app with auth enabled
        from app.main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as test_client:
            response = test_client.post("/v1/chat/completions", json={
                "model": "gemini-2.0-flash",
                "messages": [{"role": "user", "content": "test"}]
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Reset for other tests
        os.environ["API_AUTH_ENABLED"] = "false"
    
    def test_protected_endpoint_with_valid_api_key(self, client, api_headers):
        """Test that protected endpoints accept valid API key."""
        # Enable auth for this test
        os.environ["API_AUTH_ENABLED"] = "true"
        
        from app.main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as test_client:
            # This will fail because Gemini client is not initialized, but should not be 401
            response = test_client.post(
                "/v1/chat/completions",
                json={
                    "model": "gemini-2.0-flash",
                    "messages": [{"role": "user", "content": "test"}]
                },
                headers=api_headers
            )
            
            # Should not be unauthorized (may be 503 or other error)
            assert response.status_code != status.HTTP_401_UNAUTHORIZED
        
        # Reset for other tests
        os.environ["API_AUTH_ENABLED"] = "false"
    
    def test_invalid_api_key(self, client):
        """Test that invalid API key is rejected."""
        os.environ["API_AUTH_ENABLED"] = "true"
        
        from app.main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as test_client:
            response = test_client.post(
                "/v1/chat/completions",
                json={
                    "model": "gemini-2.0-flash",
                    "messages": [{"role": "user", "content": "test"}]
                },
                headers={"X-API-Key": "invalid-key"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        os.environ["API_AUTH_ENABLED"] = "false"
