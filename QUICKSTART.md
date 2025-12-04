# Quick Start Guide

## 🚀 Getting Started with WebAI-to-API

This guide will help you get WebAI-to-API up and running quickly.

---

## Prerequisites

- Python 3.10 or higher
- Poetry (recommended) or pip
- A modern web browser (Chrome, Firefox, Brave, Edge, or Safari)
- Gemini account (logged in via browser)

---

## Installation

### Option 1: Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/Amm1rr/WebAI-to-API.git
cd WebAI-to-API

# Install dependencies
poetry install

# Install development dependencies (for testing)
poetry install --with dev
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/Amm1rr/WebAI-to-API.git
cd WebAI-to-API

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### 1. Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

### 2. Edit `.env` File

Open `.env` and configure:

```env
# Required: Generate a secure API key
API_KEYS=your-secret-api-key-min-32-characters-long

# Optional: Specify allowed origins (for production)
ALLOWED_ORIGINS=http://localhost:3000

# Optional: Configure rate limiting
RATE_LIMIT_PER_MINUTE=60

# Optional: Gemini cookies (leave empty for auto-detection)
GEMINI_COOKIE_1PSID=
GEMINI_COOKIE_1PSIDTS=
```

### 3. Generate API Key

```python
# Run this in Python to generate a secure API key
import secrets
print(secrets.token_urlsafe(32))
```

Copy the generated key to your `.env` file.

---

## Running the Server

### Start the Server

```bash
# With Poetry
poetry run python src/run.py

# With pip
python src/run.py

# With custom host/port
python src/run.py --host 0.0.0.0 --port 8080
```

### Switch Between Modes

While the server is running:
- Press `1` + Enter for **WebAI mode** (Gemini, faster)
- Press `2` + Enter for **gpt4free mode** (multiple LLMs)
- Press `Ctrl+C` to quit

---

## Testing the API

### 1. Check Health

```bash
curl http://localhost:6969/health
```

### 2. Make a Chat Request

```bash
curl -X POST http://localhost:6969/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ]
  }'
```

### 3. Test Streaming

```bash
curl -X POST http://localhost:6969/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [
      {"role": "user", "content": "Tell me a story"}
    ],
    "stream": true
  }'
```

---

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:6969/docs
- **ReDoc**: http://localhost:6969/redoc

---

## Common Issues

### Issue: "Gemini client is not initialized"

**Solution:**
1. Make sure you're logged into Gemini in your browser
2. Check that the correct browser is specified in `.env`:
   ```env
   BROWSER_NAME=chrome  # or firefox, brave, edge, safari
   ```
3. Try manually setting cookies in `.env`

### Issue: "Invalid or missing API key"

**Solution:**
1. Ensure you've set `API_KEYS` in `.env`
2. Include the `X-API-Key` header in your requests
3. Verify the key matches exactly

### Issue: "Rate limit exceeded"

**Solution:**
1. Wait for the rate limit to reset (check `X-RateLimit-Reset` header)
2. Increase the limit in `.env`:
   ```env
   RATE_LIMIT_PER_MINUTE=120
   ```
3. Or disable rate limiting (not recommended for production):
   ```env
   RATE_LIMIT_ENABLED=false
   ```

### Issue: CORS errors

**Solution:**
Add your frontend origin to `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://myapp.com
```

---

## Next Steps

- Read [SECURITY.md](SECURITY.md) for production deployment
- Read [TESTING.md](TESTING.md) to run tests
- Check [README.md](README.md) for detailed documentation
- Explore the API at `/docs`

---

## Getting Help

- **Issues**: https://github.com/Amm1rr/WebAI-to-API/issues
- **Discussions**: https://github.com/Amm1rr/WebAI-to-API/discussions
- **Documentation**: https://github.com/Amm1rr/WebAI-to-API

---

## Quick Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys | (none) |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute | `60` |
| `BROWSER_NAME` | Browser for cookies | `chrome` |
| `GEMINI_DEFAULT_MODEL` | Default Gemini model | `gemini-2.0-flash` |

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/gemini` | POST | New Gemini conversation |
| `/gemini-chat` | POST | Persistent Gemini chat |
| `/docs` | GET | API documentation |
