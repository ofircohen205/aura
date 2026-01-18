"""
Redis Client

Provides Redis client for authentication and other services.
Uses connection pooling and handles errors gracefully.
"""

import os
from typing import Any

from loguru import logger

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_AUTH_DB = int(os.getenv("REDIS_AUTH_DB", "2"))  # Use DB 2 for auth tokens
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# Redis client (lazy initialization)
_redis_client: Any | None = None
_redis_available = False


def _get_redis_url() -> str:
    """
    Get Redis URL for authentication tokens.

    Returns:
        Redis URL string with appropriate database
    """
    # If REDIS_URL contains a database number, replace it
    if "/" in REDIS_URL and REDIS_URL.split("/")[-1].isdigit():
        base_url = REDIS_URL.rsplit("/", 1)[0]
        return f"{base_url}/{REDIS_AUTH_DB}"
    return f"{REDIS_URL}/{REDIS_AUTH_DB}"


async def get_redis_client():
    """
    Get or create Redis client with connection pooling.

    Returns:
        Redis client instance or None if Redis is unavailable
    """
    global _redis_client, _redis_available

    if not REDIS_ENABLED:
        return None

    if _redis_client is not None:
        return _redis_client

    try:
        import redis.asyncio as redis  # type: ignore[import-untyped]
        from redis.asyncio.connection import ConnectionPool  # type: ignore[import-untyped]

        redis_url = _get_redis_url()
        pool = ConnectionPool.from_url(
            redis_url,
            max_connections=10,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )

        _redis_client = redis.Redis(connection_pool=pool)
        _redis_available = True
        logger.info(
            "Redis client initialized for authentication",
            extra={"redis_url": redis_url.split("@")[-1]},
        )
        return _redis_client

    except ImportError:
        logger.warning("redis package not installed, Redis features disabled")
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Redis client, Redis features disabled: {e}",
            exc_info=True,
        )
        _redis_available = False
        return None


async def test_redis_connection() -> bool:
    """
    Test Redis connection availability.

    Returns:
        True if Redis is available and connected, False otherwise
    """
    if not REDIS_ENABLED:
        return False

    try:
        client = await get_redis_client()
        if client is None:
            return False
        await client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis connection test failed: {e}")
        return False
