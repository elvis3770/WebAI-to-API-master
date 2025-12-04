# Security Policy

## 🔒 Security Best Practices for WebAI-to-API

This document outlines security considerations and best practices for deploying and using WebAI-to-API.

---

## API Key Management

### Generating Secure API Keys

API keys should be:
- **At least 32 characters long**
- **Randomly generated** using cryptographically secure methods
- **Unique** for each client/user

**Example generation (Python):**
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"Generated API Key: {api_key}")
```

### Storing API Keys

✅ **DO:**
- Store API keys in `.env` file (never commit to version control)
- Use environment variables in production
- Rotate keys periodically
- Use different keys for different environments (dev/staging/prod)

❌ **DON'T:**
- Hardcode API keys in source code
- Commit `.env` files to Git
- Share API keys in plain text
- Reuse the same key across multiple services

---

## Environment Configuration

### Production Settings

For production deployments, ensure:

```env
# .env (production)
ENVIRONMENT=production
DEBUG_MODE=false
API_AUTH_ENABLED=true
RATE_LIMIT_ENABLED=true
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

### CORS Configuration

⚠️ **Never use `ALLOWED_ORIGINS=*` in production!**

Specify exact origins:
```env
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

---

## Rate Limiting

### Recommended Settings

```env
RATE_LIMIT_PER_MINUTE=60        # Adjust based on your needs
RATE_LIMIT_ENABLED=true
```

### Monitoring Rate Limits

Check response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Cookie Security

### Gemini Cookies

Cookies are sensitive credentials. Protect them:

1. **Never log cookies** in plain text
2. **Store in `.env`** file only
3. **Rotate regularly** (every 12-24 hours recommended)
4. **Monitor expiration** using cookie manager

### Auto-Refresh Configuration

```env
COOKIE_AUTO_REFRESH=true
COOKIE_REFRESH_INTERVAL_HOURS=12
```

---

## Network Security

### HTTPS/TLS

- **Always use HTTPS** in production
- Configure TLS certificates properly
- Use reverse proxy (nginx, Caddy) for SSL termination

### Proxy Configuration

If using a proxy:
```env
HTTP_PROXY=http://127.0.0.1:2334
```

Ensure proxy is trusted and secure.

---

## Logging and Monitoring

### Secure Logging

✅ **DO log:**
- Authentication attempts (success/failure)
- Rate limit violations
- API errors
- System health metrics

❌ **DON'T log:**
- API keys
- Cookies
- User message content (unless necessary)
- Sensitive personal information

### Log Configuration

```env
LOG_LEVEL=INFO              # Use WARNING or ERROR in production
LOG_FORMAT=json             # Structured logs for production
LOG_FILE_ENABLED=true
```

---

## Deployment Security

### Docker Security

When using Docker:

```dockerfile
# Use non-root user
USER nobody

# Don't expose unnecessary ports
EXPOSE 6969

# Use secrets for sensitive data
# Mount .env as a secret, not in image
```

### Kubernetes Security

```yaml
# Use secrets for API keys
apiVersion: v1
kind: Secret
metadata:
  name: webai-secrets
type: Opaque
data:
  api-keys: <base64-encoded-keys>
```

---

## Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email security concerns to: [your-security-email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## Security Checklist

Before deploying to production:

- [ ] API keys are strong and stored in `.env`
- [ ] `API_AUTH_ENABLED=true`
- [ ] `RATE_LIMIT_ENABLED=true`
- [ ] CORS origins are restricted (not `*`)
- [ ] `DEBUG_MODE=false`
- [ ] HTTPS/TLS is configured
- [ ] Logs don't contain sensitive data
- [ ] Cookies are auto-refreshing
- [ ] All dependencies are up to date
- [ ] `.env` is in `.gitignore`

---

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
