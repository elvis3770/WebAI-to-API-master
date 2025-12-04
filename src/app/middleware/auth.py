# src/app/middleware/auth.py
"""
API Key Authentication Middleware for WebAI-to-API.

Provides secure API key-based authentication for protecting endpoints.
"""
import logging
import os
from typing import List, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# API Key header name
API_KEY_HEADER_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def get_valid_api_keys() -> List[str]:
    """
    Get list of valid API keys from environment variables.
    
    Returns:
        List of valid API keys
    """
    api_keys_str = os.getenv("API_KEYS", "")
    if not api_keys_str:
        logger.warning("No API keys configured. API authentication is disabled!")
        return []
    
    # Split by comma and strip whitespace
    keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    
    if not keys:
        logger.warning("API_KEYS environment variable is empty!")
    
    return keys


def is_public_endpoint(path: str) -> bool:
    """
    Check if an endpoint is public (doesn't require authentication).
    
    Args:
        path: Request path
        
    Returns:
        True if endpoint is public, False otherwise
    """
    public_endpoints = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/health/live",
        "/health/ready",
    ]
    
    return path in public_endpoints or path.startswith("/docs") or path.startswith("/redoc")


def verify_api_key(api_key: Optional[str]) -> bool:
    """
    Verify if the provided API key is valid.
    
    Args:
        api_key: API key to verify
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    valid_keys = get_valid_api_keys()
    
    # If no keys are configured, allow access (development mode)
    if not valid_keys:
        logger.debug("No API keys configured - allowing access")
        return True
    
    return api_key in valid_keys


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate API keys for protected endpoints.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate API key.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from next middleware/endpoint
            
        Raises:
            HTTPException: If API key is invalid or missing
        """
        # Skip authentication for public endpoints
        if is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get(API_KEY_HEADER_NAME)
        
        # Verify API key
        if not verify_api_key(api_key):
            logger.warning(
                f"Unauthorized access attempt to {request.url.path} from {request.client.host}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Log successful authentication
        logger.debug(f"Authenticated request to {request.url.path}")
        
        # Store API key in request state for potential use in endpoints
        request.state.api_key = api_key
        
        return await call_next(request)


def get_api_key_from_request(request: Request) -> Optional[str]:
    """
    Helper function to get API key from request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        API key if present, None otherwise
    """
    return getattr(request.state, "api_key", None)
