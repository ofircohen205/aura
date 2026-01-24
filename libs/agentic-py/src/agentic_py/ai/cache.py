"""
LLM Call Caching

Provides caching layer for LLM calls to reduce costs and improve performance.
Uses Redis for distributed caching. Requires Redis to be available.

This module provides a thin wrapper around a RedisCache instance.
The RedisCache should be provided by the backend application.
"""

import logging
from typing import Any, Protocol

from agentic_py.config.cache import LLM_CACHE_ENABLED, LLM_CACHE_TTL

logger = logging.getLogger(__name__)

CACHE_ENABLED = LLM_CACHE_ENABLED
CACHE_TTL = LLM_CACHE_TTL

# Global RedisCache instance (set by backend)
_redis_cache: Any | None = None


class RedisCacheProtocol(Protocol):
    """Protocol for Redis cache implementations."""

    async def get(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str | None:
        """Get cached response."""
        ...

    async def set(
        self,
        prompt: str,
        response: str,
        model: str | None = None,
        temperature: float | None = None,
        ttl: int | None = None,
    ) -> None:
        """Set cached response."""
        ...

    async def clear(self) -> None:
        """Clear all cached responses."""
        ...

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        ...


def set_redis_cache(redis_cache: RedisCacheProtocol | None) -> None:
    """
    Set the Redis cache instance to use.

    This should be called by the backend application during initialization.

    Args:
        redis_cache: RedisCache instance from backend
    """
    global _redis_cache
    _redis_cache = redis_cache
    if redis_cache is not None:
        logger.info("Redis cache instance set for LLM caching")
    else:
        logger.warning("Redis cache instance cleared")


def get_redis_cache() -> RedisCacheProtocol:
    """
    Get the Redis cache instance.

    Returns:
        RedisCache instance

    Raises:
        RuntimeError: If Redis cache is not set
    """
    if _redis_cache is None:
        raise RuntimeError(
            "Redis cache is not initialized. "
            "Call set_redis_cache() with a RedisCache instance from the backend. "
            "LLM cache requires Redis and does not support in-memory fallback."
        )
    return _redis_cache


async def get_cached_response(
    prompt: str,
    model: str | None = None,
    temperature: float | None = None,
) -> str | None:
    """
    Get cached LLM response if available and not expired.

    Requires Redis cache to be initialized via set_redis_cache().

    Args:
        prompt: The prompt text
        model: Optional model name
        temperature: Optional temperature setting

    Returns:
        Cached response if found and valid, None otherwise

    Raises:
        RuntimeError: If Redis cache is not initialized
    """
    if not CACHE_ENABLED:
        return None

    try:
        cache = get_redis_cache()
        return await cache.get(prompt, model, temperature)
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get cached response: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to get cached response: {e}. "
            "LLM cache requires Redis and does not support in-memory fallback."
        ) from e


async def set_cached_response(
    prompt: str,
    response: str,
    model: str | None = None,
    temperature: float | None = None,
) -> None:
    """
    Cache LLM response in Redis.

    Requires Redis cache to be initialized via set_redis_cache().

    Args:
        prompt: The prompt text
        response: The LLM response to cache
        model: Optional model name
        temperature: Optional temperature setting

    Raises:
        RuntimeError: If Redis cache is not initialized
    """
    if not CACHE_ENABLED:
        return

    try:
        cache = get_redis_cache()
        await cache.set(prompt, response, model, temperature, ttl=CACHE_TTL)
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to set cached response: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to set cached response: {e}. "
            "LLM cache requires Redis and does not support in-memory fallback."
        ) from e


async def clear_cache() -> None:
    """
    Clear all cached responses from Redis.

    Raises:
        RuntimeError: If Redis cache is not initialized
    """
    try:
        cache = get_redis_cache()
        await cache.clear()
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to clear cache: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to clear cache: {e}. "
            "LLM cache requires Redis and does not support in-memory fallback."
        ) from e


async def get_cache_stats() -> dict[str, Any]:
    """
    Get cache statistics from Redis.

    Returns:
        Dictionary with cache statistics

    Raises:
        RuntimeError: If Redis cache is not initialized
    """
    try:
        cache = get_redis_cache()
        stats = await cache.get_stats()
        stats["enabled"] = CACHE_ENABLED
        stats["ttl_seconds"] = CACHE_TTL
        return stats
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get cache stats: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to get cache stats: {e}. "
            "LLM cache requires Redis and does not support in-memory fallback."
        ) from e
