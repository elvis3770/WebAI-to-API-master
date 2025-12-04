# src/app/endpoints/health.py
"""
Health check endpoints for monitoring and observability.
"""
import time
import os
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.services.gemini_client import get_gemini_client
from app.config import ENVIRONMENT, get_env

router = APIRouter()

# Store startup time
_startup_time = time.time()


def get_uptime() -> float:
    """Get application uptime in seconds."""
    return time.time() - _startup_time


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if the application is running.
    """
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "uptime_seconds": round(get_uptime(), 2)
    }


@router.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is alive (can handle requests).
    """
    return {"status": "alive"}


@router.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if the application is ready to serve traffic.
    Checks if all required services are initialized.
    """
    checks = {}
    all_ready = True
    
    # Check Gemini client
    gemini_client = get_gemini_client()
    checks["gemini_client"] = "ready" if gemini_client else "not_initialized"
    if not gemini_client:
        all_ready = False
    
    # Check environment configuration
    checks["environment"] = ENVIRONMENT
    
    # Overall status
    overall_status = "ready" if all_ready else "not_ready"
    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "checks": checks,
            "uptime_seconds": round(get_uptime(), 2)
        }
    )


@router.get("/metrics", tags=["Health"])
async def metrics():
    """
    Basic metrics endpoint.
    Returns simple application metrics.
    """
    return {
        "uptime_seconds": round(get_uptime(), 2),
        "environment": ENVIRONMENT,
        "gemini_available": get_gemini_client() is not None,
        "version": "0.5.0"
    }
