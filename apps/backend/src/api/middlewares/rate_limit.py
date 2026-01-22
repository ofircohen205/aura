"""
Rate Limiting Middleware

Provides rate limiting for API endpoints to prevent abuse and ensure fair usage.
Uses token bucket algorithm with Redis for distributed rate limiting.
Falls back to disabled rate limiting if Redis is unavailable.
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import get_settings
from core.metrics import metrics_helper, rate_limit_hits_total, rate_limit_requests_total
from services.redis import get_rate_limit_service, get_redis_client_manager

settings = get_settings()


def _get_client_id(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Uses IP address as primary identifier. In production, could use API key or user ID.

    Args:
        request: FastAPI request object

    Returns:
        Client identifier string
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key[:8]}"

    if request.client:
        return f"ip:{request.client.host}"

    return "unknown"


def _get_endpoint_key(path: str, endpoint_limits: dict[str, dict[str, int]]) -> str:
    """
    Get endpoint key for rate limiting configuration.

    Args:
        path: Request path
        endpoint_limits: Dictionary of endpoint patterns to rate limit configs

    Returns:
        Endpoint key for rate limit lookup
    """
    if path in endpoint_limits:
        return path

    for endpoint in sorted(endpoint_limits.keys(), key=len, reverse=True):
        if path.startswith(endpoint):
            return endpoint

    return "/api/v1/workflows"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API endpoints.

    Uses Redis for distributed rate limiting. Falls back to disabled rate limiting
    if Redis is unavailable (logs warning).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        if not settings.rate_limit_enabled:
            return await call_next(request)

        if request.url.path in ("/health", "/health/cache", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        manager = get_redis_client_manager()
        if settings.rate_limit_redis_enabled and not await manager.test_connection(
            settings.redis_rate_limit_db
        ):
            logger.warning(
                "Rate limiting disabled: Redis unavailable. "
                "Set RATE_LIMIT_REDIS_ENABLED=false to suppress this warning."
            )
            return await call_next(request)

        client_id = _get_client_id(request)
        endpoint = _get_endpoint_key(request.url.path, settings.rate_limit_endpoints)

        metrics_helper.inc_counter(rate_limit_requests_total, endpoint=endpoint)

        limit_config = settings.rate_limit_endpoints.get(
            endpoint,
            {"requests": settings.rate_limit_requests, "window": settings.rate_limit_window},
        )

        rate_limit_service = get_rate_limit_service()
        token_consumed = await rate_limit_service.consume_token(
            client_id,
            endpoint,
            limit_config["requests"],
            limit_config["window"],
            settings.rate_limit_redis_enabled,
        )

        if not token_consumed:
            metrics_helper.inc_counter(
                rate_limit_hits_total, endpoint=endpoint, client_id=client_id
            )

            tokens = await rate_limit_service.refill_tokens(
                client_id,
                endpoint,
                limit_config["requests"],
                limit_config["window"],
                settings.rate_limit_redis_enabled,
            )

            correlation_id = getattr(request.state, "correlation_id", None)
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "correlation_id": correlation_id,
                    "client_id": client_id,
                    "endpoint": endpoint,
                    "limit": limit_config["requests"],
                    "window": limit_config["window"],
                    "remaining": int(tokens),
                    "method": request.method,
                    "path": request.url.path,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Limit: {limit_config['requests']} requests per {limit_config['window']} seconds.",
                headers={
                    "X-RateLimit-Limit": str(limit_config["requests"]),
                    "X-RateLimit-Window": str(limit_config["window"]),
                    "X-RateLimit-Remaining": str(int(tokens)),
                    "Retry-After": str(limit_config["window"]),
                },
            )

        response = await call_next(request)

        tokens = await rate_limit_service.refill_tokens(
            client_id,
            endpoint,
            limit_config["requests"],
            limit_config["window"],
            settings.rate_limit_redis_enabled,
        )

        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
        response.headers["X-RateLimit-Window"] = str(limit_config["window"])
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))

        correlation_id = getattr(request.state, "correlation_id", None)
        logger.debug(
            "Rate limit check passed",
            extra={
                "correlation_id": correlation_id,
                "client_id": client_id,
                "endpoint": endpoint,
                "remaining": int(tokens),
                "limit": limit_config["requests"],
                "method": request.method,
                "path": request.url.path,
            },
        )

        return response
