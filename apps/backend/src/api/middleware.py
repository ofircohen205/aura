"""
API Middleware

FastAPI middleware for security headers and rate limiting.
"""

import os
import time
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Adds headers to protect against:
    - XSS attacks (X-Content-Type-Options, X-Frame-Options)
    - Clickjacking (X-Frame-Options)
    - MIME type sniffing (X-Content-Type-Options)
    - Protocol downgrade attacks (Strict-Transport-Security in production)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security headers to response."""
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (basic)
        # Can be customized per environment
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), " "microphone=(), " "camera=(), " "payment=(), " "usb=()"
        )

        return response


# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # Requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # Time window in seconds
RATE_LIMIT_REDIS_URL = os.getenv(
    "RATE_LIMIT_REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/1")
)
RATE_LIMIT_REDIS_ENABLED = os.getenv("RATE_LIMIT_REDIS_ENABLED", "true").lower() == "true"

# Per-endpoint rate limits (requests per window)
ENDPOINT_LIMITS: dict[str, dict[str, int]] = {
    "/api/v1/workflows/struggle": {"requests": 50, "window": 60},
    "/api/v1/workflows/audit": {"requests": 30, "window": 60},
    "/api/v1/workflows": {"requests": 100, "window": 60},  # Default for all workflow endpoints
}

# Redis client (lazy initialization)
_redis_client = None
_redis_available = False


def _get_redis_client():
    """
    Get or create Redis client for rate limiting.

    Returns:
        Redis client instance or None if Redis is unavailable
    """
    global _redis_client, _redis_available

    if not RATE_LIMIT_REDIS_ENABLED:
        return None

    if _redis_client is not None:
        return _redis_client

    try:
        import redis.asyncio as redis  # type: ignore[import-untyped]
        from redis.asyncio.connection import ConnectionPool  # type: ignore[import-untyped]

        pool = ConnectionPool.from_url(
            RATE_LIMIT_REDIS_URL,
            max_connections=10,
            decode_responses=True,
        )

        _redis_client = redis.Redis(connection_pool=pool)
        _redis_available = True
        logger.info(
            "Redis client initialized for rate limiting",
            extra={"redis_url": RATE_LIMIT_REDIS_URL.split("@")[-1]},
        )
        return _redis_client

    except ImportError:
        logger.warning("redis package not installed, rate limiting disabled")
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Redis for rate limiting, disabling: {e}", exc_info=True
        )
        _redis_available = False
        return None


async def _test_redis_connection() -> bool:
    """
    Test Redis connection availability.

    Returns:
        True if Redis is available and connected, False otherwise
    """
    if not RATE_LIMIT_REDIS_ENABLED:
        return False

    try:
        client = _get_redis_client()
        if client is None:
            return False
        await client.ping()
        return True
    except Exception:
        return False


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


def _get_endpoint_key(path: str) -> str:
    """
    Get endpoint key for rate limiting configuration.

    Args:
        path: Request path

    Returns:
        Endpoint key for rate limit lookup
    """
    # Check for exact match first
    if path in ENDPOINT_LIMITS:
        return path

    # Check for prefix match (e.g., /api/v1/workflows matches /api/v1/workflows/audit)
    for endpoint, _ in sorted(ENDPOINT_LIMITS.items(), key=len, reverse=True):
        if path.startswith(endpoint):
            return endpoint

    # Default to base path
    return "/api/v1/workflows"


async def _refill_tokens_redis(
    client_id: str, endpoint: str, max_tokens: int, window: int
) -> float:
    """
    Refill token bucket using Redis (distributed token bucket algorithm).

    Args:
        client_id: Client identifier
        endpoint: Endpoint path
        max_tokens: Maximum tokens in bucket
        window: Time window in seconds

    Returns:
        Current number of tokens after refill
    """
    client = _get_redis_client()
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


async def _consume_token_redis(client_id: str, endpoint: str) -> bool:
    """
    Consume a token from the Redis bucket.

    Args:
        client_id: Client identifier
        endpoint: Endpoint path

    Returns:
        True if token was consumed, False if bucket is empty
    """
    limit_config = ENDPOINT_LIMITS.get(
        endpoint, {"requests": RATE_LIMIT_REQUESTS, "window": RATE_LIMIT_WINDOW}
    )
    max_tokens = limit_config["requests"]
    window = limit_config["window"]

    # Refill tokens
    tokens = await _refill_tokens_redis(client_id, endpoint, max_tokens, window)

    if tokens >= 1.0:
        # Consume one token
        client = _get_redis_client()
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
        # Skip rate limiting if disabled
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health checks and other system endpoints
        if request.url.path in ("/health", "/health/cache", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # Only rate limit API endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Check Redis availability
        if not _redis_available and RATE_LIMIT_REDIS_ENABLED:
            # Test connection on first request
            if await _test_redis_connection():
                pass  # Connection successful
            else:
                logger.warning(
                    "Rate limiting disabled: Redis unavailable. "
                    "Set RATE_LIMIT_REDIS_ENABLED=false to suppress this warning."
                )
                return await call_next(request)

        client_id = _get_client_id(request)
        endpoint = _get_endpoint_key(request.url.path)

        # Check rate limit
        if not await _consume_token_redis(client_id, endpoint):
            limit_config = ENDPOINT_LIMITS.get(
                endpoint, {"requests": RATE_LIMIT_REQUESTS, "window": RATE_LIMIT_WINDOW}
            )

            # Get remaining tokens for header
            tokens = await _refill_tokens_redis(
                client_id, endpoint, limit_config["requests"], limit_config["window"]
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
        limit_config = ENDPOINT_LIMITS.get(
            endpoint, {"requests": RATE_LIMIT_REQUESTS, "window": RATE_LIMIT_WINDOW}
        )
        tokens = await _refill_tokens_redis(
            client_id, endpoint, limit_config["requests"], limit_config["window"]
        )

        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
        response.headers["X-RateLimit-Window"] = str(limit_config["window"])
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))

        return response
