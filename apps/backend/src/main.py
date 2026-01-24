"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import text

# Import conf first to set up paths
import conf  # noqa: F401
from api.exceptions import (
    BaseApplicationException,
    application_exception_handler,
    generic_exception_handler,
    http_exception_handler,
)
from api.middlewares import CSRFProtectionMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from api.middlewares.logging import CorrelationIDMiddleware, RequestLoggingMiddleware
from api.v1.audit.endpoints import create_audit_app
from api.v1.auth import create_auth_app
from api.v1.events.endpoints import create_events_app
from api.v1.rag import create_rag_app
from api.v1.workflows.endpoints import create_workflows_app
from core.config import get_settings
from core.logging import setup_logging
from db.database import async_engine, close_db, init_db

# Initialize logging
setup_logging()


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    await init_db()

    # Initialize Redis cache for LLM caching
    try:
        from agentic_py.ai.cache import set_redis_cache
        from agentic_py.config.cache import LLM_CACHE_ENABLED, LLM_CACHE_TTL, REDIS_KEY_PREFIX

        from services.redis import RedisCache

        if LLM_CACHE_ENABLED:
            redis_cache = RedisCache(
                redis_client=None,  # Will use get_redis_client_manager internally
                key_prefix=REDIS_KEY_PREFIX,
                default_ttl=LLM_CACHE_TTL,
            )
            set_redis_cache(redis_cache)
            logger.info("Redis cache initialized for LLM caching")
        else:
            logger.debug("LLM cache is disabled")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache for LLM: {e}", exc_info=True)

    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add middleware (order matters - first added is outermost)
# CORS must be early to handle preflight requests and add headers to error responses
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
if settings.csrf_protection_enabled:
    app.add_middleware(CSRFProtectionMiddleware)  # CSRF protection
app.add_middleware(RateLimitMiddleware)  # Rate limiting before logging
app.add_middleware(RequestLoggingMiddleware)

# Register global exception handlers (order matters - more specific first)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(BaseApplicationException, application_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Mount Sub-Applications
auth_app = create_auth_app()
workflows_app = create_workflows_app()
events_app = create_events_app()
audit_app = create_audit_app()
rag_app = create_rag_app()

app.mount("/api/v1/auth", auth_app)
app.mount("/api/v1/workflows", workflows_app)
app.mount("/api/v1/events", events_app)
app.mount("/api/v1/audit", audit_app)
app.mount("/api/v1/rag", rag_app)


# Prometheus metrics
try:
    from prometheus_client import make_asgi_app

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
except ImportError:
    # Prometheus client not installed, metrics disabled
    pass


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
        from agentic_py.ai.cache import get_cache_stats

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


@app.get("/health/redis")
async def redis_health_check():
    """
    Health check endpoint for Redis connectivity.

    Checks connectivity for both auth and rate limiting Redis databases.

    Returns:
        dict: Redis health status with connection details for each database
    """
    from core.config import get_settings
    from services.redis import get_redis_client_manager

    settings = get_settings()
    manager = get_redis_client_manager()

    health_status = {
        "status": "ok",
        "redis": {
            "auth_db": {
                "database": settings.redis_auth_db,
                "connected": False,
            },
            "rate_limit_db": {
                "database": settings.redis_rate_limit_db,
                "connected": False,
            },
        },
    }

    # Check auth database connection
    try:
        auth_connected = await manager.test_connection(settings.redis_auth_db)
        health_status["redis"]["auth_db"]["connected"] = auth_connected
        if not auth_connected:
            health_status["status"] = "degraded"
            logger.warning(f"Redis auth database {settings.redis_auth_db} is not connected")
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["redis"]["auth_db"]["error"] = str(e)
        logger.error(f"Redis auth database health check failed: {e}", exc_info=True)

    # Check rate limiting database connection
    try:
        rate_limit_connected = await manager.test_connection(settings.redis_rate_limit_db)
        health_status["redis"]["rate_limit_db"]["connected"] = rate_limit_connected
        if not rate_limit_connected:
            health_status["status"] = "degraded"
            logger.warning(
                f"Redis rate limit database {settings.redis_rate_limit_db} is not connected"
            )
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["redis"]["rate_limit_db"]["error"] = str(e)
        logger.error(f"Redis rate limit database health check failed: {e}", exc_info=True)

    # If both databases are unavailable, return 503
    if (
        not health_status["redis"]["auth_db"]["connected"]
        and not health_status["redis"]["rate_limit_db"]["connected"]
    ):
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - Redis connections failed for all databases",
        )

    return health_status
