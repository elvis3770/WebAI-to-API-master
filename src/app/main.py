# src/app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.services.gemini_client import get_gemini_client
from app.services.session_manager import init_session_managers
from app.logger import logger
from app.config import get_env, get_env_bool

# Import middleware
from app.middleware.auth import APIKeyMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Import endpoint routers
from app.endpoints import gemini, chat, google_generative, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes services on startup and cleanup on shutdown.
    """
    logger.info("Starting WebAI-to-API application...")
    
    # Initialization logic is handled by the `run.py` script before the app starts.
    # We only initialize session managers here if the client was created successfully.
    if get_gemini_client():
        init_session_managers()
        logger.info("Session managers initialized for WebAI-to-API.")
    
    logger.info("Application startup complete.")
    
    yield
    
    # Shutdown logic: No explicit client closing is needed anymore.
    # The underlying HTTPX client manages its connection pool automatically.
    logger.info("Application shutdown complete.")


# Create FastAPI app with metadata
app = FastAPI(
    title="WebAI-to-API",
    description="Modular web server to expose browser-based LLMs as API endpoints",
    version="0.5.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS from environment variables
def get_cors_origins():
    """Get CORS origins from environment variable."""
    origins_str = get_env("ALLOWED_ORIGINS", "*")
    if origins_str == "*":
        return ["*"]
    return [origin.strip() for origin in origins_str.split(",") if origin.strip()]


cors_origins = get_cors_origins()
logger.info(f"CORS configured with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add security middleware
# Note: Order matters! Auth should come before rate limiting
auth_enabled = get_env_bool("API_AUTH_ENABLED", True)
if auth_enabled:
    app.add_middleware(APIKeyMiddleware)
    logger.info("API Key authentication enabled")
else:
    logger.warning("API Key authentication is DISABLED - not recommended for production!")

# Add rate limiting middleware
rate_limit_enabled = get_env_bool("RATE_LIMIT_ENABLED", True)
if rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting enabled")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    debug_mode = get_env_bool("DEBUG_MODE", False)
    
    if debug_mode:
        detail = f"{type(exc).__name__}: {str(exc)}"
    else:
        detail = "An internal error occurred. Please try again later."
    
    return JSONResponse(
        status_code=500,
        content={"detail": detail}
    )


# Register the endpoint routers for WebAI-to-API
app.include_router(health.router, tags=["Health"])
app.include_router(gemini.router, tags=["Gemini"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(google_generative.router, tags=["Google Generative AI"])


# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "WebAI-to-API",
        "version": "0.5.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }
