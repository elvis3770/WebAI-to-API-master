# src/app/middleware/rate_limit.py
"""
Rate Limiting Middleware for WebAI-to-API.

Provides request rate limiting to prevent abuse and ensure fair usage.
"""
import logging
import time
import os
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    For production with multiple instances, consider using Redis.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        # Store: {identifier: [(timestamp1, timestamp2, ...)]}
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, str]]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (IP address or API key)
            
        Returns:
            Tuple of (is_allowed, headers_dict)
        """
        current_time = time.time()
        
        # Clean old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_size
        ]
        
        # Count requests in current window
        request_count = len(self.requests[identifier])
        
        # Calculate remaining requests
        remaining = max(0, self.requests_per_minute - request_count)
        
        # Calculate reset time (next minute)
        if self.requests[identifier]:
            oldest_request = min(self.requests[identifier])
            reset_time = int(oldest_request + self.window_size)
        else:
            reset_time = int(current_time + self.window_size)
        
        # Prepare rate limit headers
        headers = {
            "X-RateLimit-Limit": str(self.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }
        
        # Check if limit exceeded
        if request_count >= self.requests_per_minute:
            retry_after = reset_time - int(current_time)
            headers["Retry-After"] = str(max(1, retry_after))
            return False, headers
        
        # Add current request to the list
        self.requests[identifier].append(current_time)
        
        return True, headers
    
    def cleanup_old_entries(self):
        """
        Cleanup old entries to prevent memory leaks.
        Should be called periodically.
        """
        current_time = time.time()
        identifiers_to_remove = []
        
        for identifier, timestamps in self.requests.items():
            # Remove timestamps outside the window
            self.requests[identifier] = [
                ts for ts in timestamps
                if current_time - ts < self.window_size
            ]
            
            # Mark empty entries for removal
            if not self.requests[identifier]:
                identifiers_to_remove.append(identifier)
        
        # Remove empty entries
        for identifier in identifiers_to_remove:
            del self.requests[identifier]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API requests.
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute (from env if not provided)
        """
        super().__init__(app)
        
        # Get rate limit from environment or use provided value
        if requests_per_minute is None:
            requests_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
        self.rate_limiter = RateLimiter(requests_per_minute)
        
        if self.enabled:
            logger.info(f"Rate limiting enabled: {requests_per_minute} requests/minute")
        else:
            logger.info("Rate limiting disabled")
    
    def get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Uses API key if available, otherwise uses IP address.
        
        Args:
            request: FastAPI request
            
        Returns:
            Unique identifier string
        """
        # Try to get API key from request state (set by auth middleware)
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            return f"key:{api_key[:8]}"  # Use first 8 chars for privacy
        
        # Fall back to IP address
        client_host = request.client.host if request.client else "unknown"
        
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_host = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_host}"
    
    def is_exempt_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is exempt from rate limiting.
        
        Args:
            path: Request path
            
        Returns:
            True if exempt, False otherwise
        """
        exempt_endpoints = [
            "/health",
            "/health/live",
            "/health/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        return path in exempt_endpoints or path.startswith("/docs") or path.startswith("/redoc")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from next middleware/endpoint
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Skip if rate limiting is disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip exempt endpoints
        if self.is_exempt_endpoint(request.url.path):
            return await call_next(request)
        
        # Get identifier for this request
        identifier = self.get_identifier(request)
        
        # Check rate limit
        is_allowed, headers = self.rate_limiter.is_allowed(identifier)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers=headers,
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response
