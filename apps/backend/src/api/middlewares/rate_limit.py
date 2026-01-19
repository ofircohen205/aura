"""
Rate Limiting Middleware

Provides rate limiting for API endpoints to prevent abuse and ensure fair usage.
Uses token bucket algorithm with Redis for distributed rate limiting.
Falls back to disabled rate limiting if Redis is unavailable.
"""

import time
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import get_settings
from services.redis import REDIS_RATE_LIMIT_DB, get_redis_client, test_redis_connection

# Import metrics (optional, fails gracefully if prometheus_client not installed)
try:
    from core.metrics import rate_limit_hits_total, rate_limit_requests_total

    METRICS_ENABLED = True
except ImportError:
    # Metrics not available
    METRICS_ENABLED = False
    rate_limit_hits_total = None
    rate_limit_requests_total = None


def _get_client_id(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Uses IP address as primary identifier. In production, could use API key or user ID.

    Args:
        request: FastAPI request object

    Returns:
        Client identifier string
    """
    # Try to get API key from header first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key[:8]}"  # Use first 8 chars for privacy

    # Fall back to IP address
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
    # Check for exact match first
    if path in endpoint_limits:
        return path

    # Check for prefix match (e.g., /api/v1/workflows matches /api/v1/workflows/audit)
    # Sort by length (longest first) to match most specific patterns first
    for endpoint in sorted(endpoint_limits.keys(), key=len, reverse=True):
        if path.startswith(endpoint):
            return endpoint

    # Default to base API path if no match found
    return "/api/v1/workflows"


async def _refill_tokens_redis(
    client_id: str,
    endpoint: str,
    max_tokens: int,
    window: int,
    redis_enabled: bool,
) -> float:
    """
    Refill token bucket using Redis (distributed token bucket algorithm).

    Args:
        client_id: Client identifier
        endpoint: Endpoint path
        max_tokens: Maximum tokens in bucket
        window: Time window in seconds
        redis_enabled: Whether Redis is enabled for rate limiting

    Returns:
        Current number of tokens after refill
    """
    if not redis_enabled:
        return 0.0

    client = await get_redis_client(REDIS_RATE_LIMIT_DB)
    if client is None:
        return 0.0

    try:
        key = f"rate_limit:{client_id}:{endpoint}"
        current_time = time.time()

        # Use Redis pipeline for atomic operations
        pipe = client.pipeline()
        pipe.hgetall(key)
        results = await pipe.execute()

        bucket_data = results[0] if results else {}

        if not bucket_data:
            # Initialize bucket
            tokens = float(max_tokens)
            last_refill = current_time
        else:
            tokens = float(bucket_data.get("tokens", max_tokens))
            last_refill = float(bucket_data.get("last_refill", current_time))

        elapsed = current_time - last_refill

        # Refill tokens based on elapsed time
        # Tokens refill at rate of max_tokens per window
        refill_rate = max_tokens / window
        tokens_to_add = elapsed * refill_rate
        new_tokens = min(tokens + tokens_to_add, max_tokens)

        # Update bucket in Redis with expiration
        pipe = client.pipeline()
        pipe.hset(key, mapping={"tokens": str(new_tokens), "last_refill": str(current_time)})
        pipe.expire(key, window * 2)  # Expire after 2x window to allow cleanup
        await pipe.execute()

        return new_tokens

    except Exception as e:
        logger.warning(f"Redis rate limit operation failed: {e}", exc_info=True)
        return 0.0


async def _consume_token_redis(
    client_id: str,
    endpoint: str,
    endpoint_limits: dict[str, dict[str, int]],
    default_requests: int,
    default_window: int,
    redis_enabled: bool,
) -> bool:
    """
    Consume a token from the Redis bucket.

    Args:
        client_id: Client identifier
        endpoint: Endpoint path
        endpoint_limits: Dictionary of endpoint patterns to rate limit configs
        default_requests: Default number of requests per window
        default_window: Default time window in seconds
        redis_enabled: Whether Redis is enabled for rate limiting

    Returns:
        True if token was consumed, False if bucket is empty
    """
    limit_config = endpoint_limits.get(
        endpoint, {"requests": default_requests, "window": default_window}
    )
    max_tokens = limit_config["requests"]
    window = limit_config["window"]

    # Refill tokens
    tokens = await _refill_tokens_redis(client_id, endpoint, max_tokens, window, redis_enabled)

    if tokens >= 1.0:
        # Consume one token
        if not redis_enabled:
            return False

        client = await get_redis_client(REDIS_RATE_LIMIT_DB)
        if client is None:
            return False

        try:
            key = f"rate_limit:{client_id}:{endpoint}"
            current_time = time.time()

            pipe = client.pipeline()
            pipe.hset(key, "tokens", str(tokens - 1.0))
            pipe.hset(key, "last_refill", str(current_time))
            pipe.expire(key, window * 2)
            await pipe.execute()

            return True
        except Exception as e:
            logger.warning(f"Redis token consumption failed: {e}", exc_info=True)
            return False

    return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API endpoints.

    Uses Redis for distributed rate limiting. Falls back to disabled rate limiting
    if Redis is unavailable (logs warning).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        settings = get_settings()

        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for health checks and other system endpoints
        if request.url.path in ("/health", "/health/cache", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # Only rate limit API endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Check Redis availability
        if settings.rate_limit_redis_enabled and not await test_redis_connection(
            REDIS_RATE_LIMIT_DB
        ):
            logger.warning(
                "Rate limiting disabled: Redis unavailable. "
                "Set RATE_LIMIT_REDIS_ENABLED=false to suppress this warning."
            )
            return await call_next(request)

        client_id = _get_client_id(request)
        endpoint = _get_endpoint_key(request.url.path, settings.rate_limit_endpoints)

        # Track rate limit requests
        if METRICS_ENABLED:
            rate_limit_requests_total.labels(endpoint=endpoint).inc()

        # Get limit configuration for this endpoint
        limit_config = settings.rate_limit_endpoints.get(
            endpoint,
            {"requests": settings.rate_limit_requests, "window": settings.rate_limit_window},
        )

        # Check rate limit
        if not await _consume_token_redis(
            client_id,
            endpoint,
            settings.rate_limit_endpoints,
            settings.rate_limit_requests,
            settings.rate_limit_window,
            settings.rate_limit_redis_enabled,
        ):
            # Track rate limit hit
            if METRICS_ENABLED:
                rate_limit_hits_total.labels(endpoint=endpoint, client_id=client_id).inc()

            # Get remaining tokens for header
            tokens = await _refill_tokens_redis(
                client_id,
                endpoint,
                limit_config["requests"],
                limit_config["window"],
                settings.rate_limit_redis_enabled,
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

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        tokens = await _refill_tokens_redis(
            client_id,
            endpoint,
            limit_config["requests"],
            limit_config["window"],
            settings.rate_limit_redis_enabled,
        )

        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
        response.headers["X-RateLimit-Window"] = str(limit_config["window"])
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))

        return response
