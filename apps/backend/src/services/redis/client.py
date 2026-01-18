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
REDIS_RATE_LIMIT_DB = int(os.getenv("REDIS_RATE_LIMIT_DB", "1"))  # Use DB 1 for rate limiting
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# Redis clients (lazy initialization) - one per database
_redis_clients: dict[int, Any] = {}
_redis_available = False


def _get_redis_url(db_number: int) -> str:
    """
    Get Redis URL for a specific database.

    Args:
        db_number: Database number to use

    Returns:
        Redis URL string with appropriate database
    """
    # If REDIS_URL contains a database number, replace it
    if "/" in REDIS_URL and REDIS_URL.split("/")[-1].isdigit():
        base_url = REDIS_URL.rsplit("/", 1)[0]
        return f"{base_url}/{db_number}"
    return f"{REDIS_URL}/{db_number}"


async def get_redis_client(db_number: int | None = None):
    """
    Get or create Redis client with connection pooling.

    Args:
        db_number: Database number to use. If None, uses REDIS_AUTH_DB (default: 2)

    Returns:
        Redis client instance or None if Redis is unavailable
    """
    global _redis_clients, _redis_available

    if not REDIS_ENABLED:
        return None

    # Default to auth database if not specified
    if db_number is None:
        db_number = REDIS_AUTH_DB

    # Return existing client if available
    if db_number in _redis_clients:
        return _redis_clients[db_number]

    try:
        import redis.asyncio as redis  # type: ignore[import-untyped]
        from redis.asyncio.connection import ConnectionPool  # type: ignore[import-untyped]

        redis_url = _get_redis_url(db_number)
        pool: ConnectionPool = ConnectionPool.from_url(
            redis_url,
            max_connections=10,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )

        client = redis.Redis(connection_pool=pool)
        _redis_clients[db_number] = client
        _redis_available = True
        logger.info(
            f"Redis client initialized for database {db_number}",
            extra={"redis_url": redis_url.split("@")[-1], "db": db_number},
        )
        return client

    except ImportError:
        logger.warning("redis package not installed, Redis features disabled")
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Redis client for database {db_number}, Redis features disabled: {e}",
            exc_info=True,
        )
        _redis_available = False
        return None


async def test_redis_connection(db_number: int | None = None) -> bool:
    """
    Test Redis connection availability.

    Args:
        db_number: Database number to test. If None, uses REDIS_AUTH_DB (default: 2)

    Returns:
        True if Redis is available and connected, False otherwise
    """
    if not REDIS_ENABLED:
        return False

    try:
        client = await get_redis_client(db_number)
        if client is None:
            return False
        await client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis connection test failed: {e}")
        return False
