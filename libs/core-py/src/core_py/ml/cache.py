"""
LLM Call Caching

Provides caching layer for LLM calls to reduce costs and improve performance.
Uses Redis for distributed caching with fallback to in-memory cache.
"""

import hashlib
import logging
import time
from typing import Any

from core_py.ml.config import (
    LLM_CACHE_ENABLED,
    LLM_CACHE_MAX_SIZE,
    LLM_CACHE_TTL,
    REDIS_CONNECTION_POOL_SIZE,
    REDIS_ENABLED,
    REDIS_KEY_PREFIX,
    REDIS_SOCKET_CONNECT_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
    REDIS_URL,
)

logger = logging.getLogger(__name__)

# Cache configuration (imported from config for consistency)
CACHE_ENABLED = LLM_CACHE_ENABLED
CACHE_TTL = LLM_CACHE_TTL
CACHE_MAX_SIZE = LLM_CACHE_MAX_SIZE

# Redis client (lazy initialization)
_redis_client: Any | None = None
_redis_available = False

# In-memory cache fallback: {cache_key: (response, timestamp)}
_memory_cache: dict[str, tuple[str, float]] = {}


def _get_redis_client():
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

        # Parse Redis URL
        from redis.asyncio.connection import ConnectionPool  # type: ignore[import-untyped]

        pool = ConnectionPool.from_url(
            REDIS_URL,
            max_connections=REDIS_CONNECTION_POOL_SIZE,
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
            decode_responses=True,  # Automatically decode responses to strings
        )

        _redis_client = redis.Redis(connection_pool=pool)
        _redis_available = True
        logger.info(
            "Redis client initialized successfully", extra={"redis_url": REDIS_URL.split("@")[-1]}
        )
        return _redis_client

    except ImportError:
        logger.warning("redis package not installed, falling back to in-memory cache")
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Redis client, falling back to in-memory cache: {e}",
            exc_info=True,
        )
        _redis_available = False
        return None


async def _test_redis_connection() -> bool:
    """
    Test Redis connection availability.

    Returns:
        True if Redis is available and connected, False otherwise
    """
    if not REDIS_ENABLED:
        return False

    try:
        client = _get_redis_client()
        if client is None:
            return False

        # Test connection with a simple ping
        await client.ping()
        return True
    except Exception as e:
        logger.debug(f"Redis connection test failed: {e}")
        return False


def _generate_cache_key(
    prompt: str, model: str | None = None, temperature: float | None = None
) -> str:
    """
    Generate cache key from prompt and model parameters.

    Args:
        prompt: The prompt text
        model: Optional model name
        temperature: Optional temperature setting

    Returns:
        SHA256 hash of the cache key (without prefix)
    """
    key_parts = [prompt]
    if model:
        key_parts.append(f"model:{model}")
    if temperature is not None:
        key_parts.append(f"temp:{temperature}")

    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode("utf-8")).hexdigest()


def _get_full_redis_key(cache_key: str) -> str:
    """
    Get full Redis key with prefix.

    Args:
        cache_key: Base cache key (SHA256 hash)

    Returns:
        Full Redis key with prefix
    """
    return f"{REDIS_KEY_PREFIX}{cache_key}"


async def get_cached_response(
    prompt: str, model: str | None = None, temperature: float | None = None
) -> str | None:
    """
    Get cached LLM response if available and not expired.

    Tries Redis first, falls back to in-memory cache if Redis is unavailable.

    Args:
        prompt: The prompt text
        model: Optional model name
        temperature: Optional temperature setting

    Returns:
        Cached response if found and valid, None otherwise
    """
    if not CACHE_ENABLED:
        return None

    cache_key = _generate_cache_key(prompt, model, temperature)

    # Try Redis first if enabled
    if REDIS_ENABLED:
        try:
            client = _get_redis_client()
            if client is not None:
                redis_key = _get_full_redis_key(cache_key)
                cached_value = await client.get(redis_key)

                if cached_value:
                    logger.debug(f"Redis cache hit for key: {cache_key[:16]}...")
                    return cached_value

        except Exception as e:
            logger.debug(f"Redis cache read failed, trying in-memory: {e}")

    # Fallback to in-memory cache
    if cache_key not in _memory_cache:
        return None

    response, timestamp = _memory_cache[cache_key]
    current_time = time.time()

    # Check if cache entry is expired
    if current_time - timestamp > CACHE_TTL:
        # Remove expired entry
        del _memory_cache[cache_key]
        logger.debug(f"In-memory cache entry expired for key: {cache_key[:16]}...")
        return None

    logger.debug(f"In-memory cache hit for key: {cache_key[:16]}...")
    return response


async def set_cached_response(
    prompt: str,
    response: str,
    model: str | None = None,
    temperature: float | None = None,
) -> None:
    """
    Cache LLM response.

    Uses Redis if available, falls back to in-memory cache.

    Args:
        prompt: The prompt text
        response: The LLM response to cache
        model: Optional model name
        temperature: Optional temperature setting
    """
    if not CACHE_ENABLED:
        return

    cache_key = _generate_cache_key(prompt, model, temperature)

    # Try Redis first if enabled
    if REDIS_ENABLED:
        try:
            client = _get_redis_client()
            if client is not None:
                redis_key = _get_full_redis_key(cache_key)
                # Set with TTL (Redis handles expiration automatically)
                await client.setex(redis_key, CACHE_TTL, response)
                logger.debug(f"Cached response in Redis for key: {cache_key[:16]}...")
                return

        except Exception as e:
            logger.debug(f"Redis cache write failed, using in-memory: {e}")

    # Fallback to in-memory cache
    # Enforce max cache size (simple LRU: remove oldest entries)
    if len(_memory_cache) >= CACHE_MAX_SIZE:
        # Remove oldest entry (simple approach - could use OrderedDict for better LRU)
        oldest_key = min(_memory_cache.keys(), key=lambda k: _memory_cache[k][1])
        del _memory_cache[oldest_key]
        logger.debug(f"In-memory cache full, removed oldest entry: {oldest_key[:16]}...")

    _memory_cache[cache_key] = (response, time.time())
    logger.debug(f"Cached response in memory for key: {cache_key[:16]}...")


async def clear_cache() -> None:
    """Clear all cached responses from both Redis and in-memory cache."""
    # Clear Redis cache
    if REDIS_ENABLED:
        try:
            client = _get_redis_client()
            if client is not None:
                # Delete all keys with our prefix
                pattern = f"{REDIS_KEY_PREFIX}*"
                keys = await client.keys(pattern)
                if keys:
                    await client.delete(*keys)
                logger.info(f"Cleared {len(keys)} entries from Redis cache")
        except Exception as e:
            logger.warning(f"Failed to clear Redis cache: {e}")

    # Clear in-memory cache
    _memory_cache.clear()
    logger.info("LLM cache cleared (Redis and in-memory)")


async def get_cache_stats() -> dict[str, Any]:
    """
    Get cache statistics from both Redis and in-memory cache.

    Returns:
        Dictionary with cache statistics
    """
    stats: dict[str, Any] = {
        "enabled": CACHE_ENABLED,
        "redis_enabled": REDIS_ENABLED,
        "redis_available": False,
        "memory_cache": {
            "total_entries": len(_memory_cache),
            "valid_entries": 0,
            "expired_entries": 0,
        },
        "redis_cache": {
            "total_entries": 0,
        },
        "max_size": CACHE_MAX_SIZE,
        "ttl_seconds": CACHE_TTL,
    }

    # Get in-memory cache stats
    current_time = time.time()
    valid_entries = sum(
        1 for _, timestamp in _memory_cache.values() if current_time - timestamp <= CACHE_TTL
    )
    stats["memory_cache"]["valid_entries"] = valid_entries
    stats["memory_cache"]["expired_entries"] = len(_memory_cache) - valid_entries

    # Get Redis cache stats
    if REDIS_ENABLED:
        try:
            client = _get_redis_client()
            if client is not None:
                # Test connection
                await client.ping()
                stats["redis_available"] = True

                # Count keys with our prefix
                pattern = f"{REDIS_KEY_PREFIX}*"
                keys = await client.keys(pattern)
                stats["redis_cache"]["total_entries"] = len(keys)
        except Exception as e:
            logger.debug(f"Failed to get Redis cache stats: {e}")
            stats["redis_available"] = False

    return stats
