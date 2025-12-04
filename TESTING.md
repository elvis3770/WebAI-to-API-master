# Testing Guide

## 🧪 Testing WebAI-to-API

This guide explains how to run tests, write new tests, and maintain test coverage.

---

## Quick Start

### Install Dependencies

```bash
# Using Poetry (recommended)
poetry install --with dev

# Using pip
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Run All Tests

```bash
# With Poetry
poetry run pytest

# With pip
pytest
```

### Run with Coverage

```bash
# Generate coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser
```

---

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_config.py              # Configuration tests
├── test_endpoints/
│   ├── test_health.py          # Health check tests
│   ├── test_chat.py            # Chat endpoint tests
│   └── test_gemini.py          # Gemini endpoint tests
├── test_middleware/
│   ├── test_auth.py            # Authentication tests
│   └── test_rate_limit.py      # Rate limiting tests
└── test_services/
    ├── test_gemini_client.py   # Gemini client tests
    └── test_session_manager.py # Session manager tests
```

---

## Writing Tests

### Basic Test Example

```python
# tests/test_endpoints/test_example.py
import pytest
from fastapi import status

class TestExampleEndpoint:
    """Test suite for example endpoint."""
    
    def test_endpoint_success(self, client):
        """Test successful request."""
        response = client.get("/example")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "result" in data
    
    def test_endpoint_error(self, client):
        """Test error handling."""
        response = client.post("/example", json={"invalid": "data"})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

### Using Fixtures

```python
def test_with_mock_client(self, client, mock_gemini_client, monkeypatch):
    """Test using mocked Gemini client."""
    # Replace real client with mock
    monkeypatch.setattr(
        "app.services.gemini_client._gemini_client",
        mock_gemini_client
    )
    
    response = client.post("/v1/chat/completions", json={
        "model": "gemini-2.0-flash",
        "messages": [{"role": "user", "content": "test"}]
    })
    
    assert response.status_code == status.HTTP_200_OK
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

---

## Available Fixtures

### `client`
FastAPI test client for making HTTP requests.

```python
def test_example(client):
    response = client.get("/health")
    assert response.status_code == 200
```

### `mock_gemini_client`
Mocked Gemini client for testing without real API calls.

```python
def test_with_mock(mock_gemini_client):
    mock_gemini_client.generate_content.return_value.text = "Test response"
```

### `api_headers`
Headers with valid API key for authenticated requests.

```python
def test_auth(client, api_headers):
    response = client.post("/protected", headers=api_headers)
    assert response.status_code != 401
```

### `sample_chat_request`
Sample chat completion request payload.

```python
def test_chat(client, sample_chat_request):
    response = client.post("/v1/chat/completions", json=sample_chat_request)
```

---

## Running Specific Tests

### By File

```bash
pytest tests/test_endpoints/test_health.py
```

### By Class

```bash
pytest tests/test_endpoints/test_health.py::TestHealthEndpoints
```

### By Function

```bash
pytest tests/test_endpoints/test_health.py::TestHealthEndpoints::test_health_check
```

### By Marker

```bash
# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

---

## Coverage Goals

- **Overall coverage**: >80%
- **Critical paths**: >90%
- **New code**: 100%

### Check Coverage

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report (detailed)
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --with dev
      
      - name: Run tests
        run: poetry run pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Best Practices

### 1. Test Independence
Each test should be independent and not rely on other tests.

```python
# ✅ Good
def test_create_user(client):
    response = client.post("/users", json={"name": "Test"})
    assert response.status_code == 201

# ❌ Bad (depends on previous test)
def test_get_user(client):
    response = client.get("/users/1")  # Assumes user 1 exists
```

### 2. Use Descriptive Names

```python
# ✅ Good
def test_authentication_fails_with_invalid_api_key(client):
    ...

# ❌ Bad
def test_auth(client):
    ...
```

### 3. Test Edge Cases

```python
def test_endpoint_with_empty_input(client):
    response = client.post("/endpoint", json={})
    assert response.status_code == 400

def test_endpoint_with_very_long_input(client):
    long_text = "a" * 10000
    response = client.post("/endpoint", json={"text": long_text})
    # Assert appropriate handling
```

### 4. Mock External Dependencies

```python
@pytest.fixture
def mock_external_api(monkeypatch):
    def mock_call(*args, **kwargs):
        return {"status": "success"}
    
    monkeypatch.setattr("module.external_api_call", mock_call)
```

---

## Troubleshooting

### Tests Fail Locally But Pass in CI

- Check environment variables
- Ensure `.env` is not affecting tests
- Verify Python version matches CI

### Slow Tests

```bash
# Find slowest tests
pytest --durations=10
```

### Flaky Tests

- Use `pytest-repeat` to run tests multiple times
- Check for race conditions in async code
- Ensure proper cleanup in fixtures

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
