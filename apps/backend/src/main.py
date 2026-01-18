"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import text

# Import conf first to set up paths
import conf  # noqa: F401
from api.middlewares import CSRFProtectionMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from api.v1.audit.endpoints import create_audit_app
from api.v1.events.endpoints import create_events_app
from api.v1.workflows.endpoints import create_workflows_app
from core.config import get_settings
from core.exceptions import (
    BaseApplicationException,
    application_exception_handler,
    generic_exception_handler,
)
from core.logging import CorrelationIDMiddleware, RequestLoggingMiddleware, setup_logging
from db.database import async_engine, close_db, init_db

# Initialize logging
setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)  # Security headers first
if settings.csrf_protection_enabled:
    app.add_middleware(CSRFProtectionMiddleware)  # CSRF protection
app.add_middleware(RateLimitMiddleware)  # Rate limiting before logging
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Register global exception handlers
app.add_exception_handler(BaseApplicationException, application_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Mount Sub-Applications
workflows_app = create_workflows_app()
events_app = create_events_app()
audit_app = create_audit_app()

app.mount("/api/v1/workflows", workflows_app)
app.mount("/api/v1/events", events_app)
app.mount("/api/v1/audit", audit_app)


@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connectivity verification.

    Returns:
        dict: Health status with database connectivity
    """
    try:
        # Check database connectivity
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error("Health check failed - database unreachable", exc_info=True)
        raise HTTPException(
            status_code=503, detail="Service unavailable - database connection failed"
        ) from e


@app.get("/health/cache")
async def cache_health_check():
    """
    Health check endpoint for LLM cache statistics.

    Returns:
        dict: Cache statistics and health status
    """
    try:
        from core_py.ml.cache import get_cache_stats

        stats = await get_cache_stats()
        return {
            "status": "ok",
            "cache": stats,
        }
    except Exception as e:
        logger.error("Cache health check failed", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }
