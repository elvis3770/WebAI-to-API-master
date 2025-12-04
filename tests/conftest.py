# tests/conftest.py
"""
Pytest configuration and shared fixtures for WebAI-to-API tests.
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment variables.
    Runs once per test session.
    """
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG_MODE"] = "true"
    os.environ["API_AUTH_ENABLED"] = "false"  # Disable auth for most tests
    os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable rate limiting for tests
    os.environ["API_KEYS"] = "test-api-key-12345678901234567890"
    os.environ["ALLOWED_ORIGINS"] = "*"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise in tests
    
    yield
    
    # Cleanup after all tests
    pass


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.
    """
    # Import here to avoid circular imports and ensure env vars are set
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_gemini_client():
    """
    Create a mock Gemini client for testing.
    """
    mock_client = Mock()
    mock_client.generate_content = AsyncMock()
    
    # Default response
    mock_response = Mock()
    mock_response.text = "This is a test response from Gemini."
    mock_client.generate_content.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_session_manager():
    """
    Create a mock session manager for testing.
    """
    mock_manager = Mock()
    mock_manager.get_response = AsyncMock()
    
    # Default response
    mock_response = Mock()
    mock_response.text = "This is a test response from session manager."
    mock_manager.get_response.return_value = mock_response
    
    return mock_manager


@pytest.fixture
def sample_chat_request():
    """
    Sample chat completion request payload.
    """
    return {
        "model": "gemini-2.0-flash",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }


@pytest.fixture
def sample_gemini_request():
    """
    Sample Gemini request payload.
    """
    return {
        "message": "What is the capital of France?",
        "model": "gemini-2.0-flash"
    }


@pytest.fixture
def api_headers():
    """
    Headers with valid API key for authenticated requests.
    """
    return {
        "X-API-Key": "test-api-key-12345678901234567890"
    }
