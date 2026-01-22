"""
Redis Cache Service

Provides caching functionality for LLM responses using Redis.
"""

import hashlib
from typing import Any

from loguru import logger

from core.config import get_settings
from services.redis.client import get_redis_client_manager

# Get LLM cache database from settings
_settings = get_settings()
REDIS_LLM_CACHE_DB = _settings.redis_llm_cache_db


class RedisCache:
    """
    Redis-based cache for LLM responses.

    Provides caching functionality using Redis with key prefixing and TTL support.
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        key_prefix: str = "aura:llm:cache:",
        default_ttl: int = 3600,
    ):
        """
        Initialize Redis cache.

        Args:
            redis_client: Optional Redis client to use. If None, creates a new client.
            key_prefix: Prefix for all cache keys
            default_ttl: Default TTL in seconds for cached items
        """
        self._redis_client = redis_client
        self._key_prefix = key_prefix
        self._default_ttl = default_ttl
        self._db_number = REDIS_LLM_CACHE_DB

    async def _get_client(self) -> Any:
        """
        Get Redis client, creating one if needed.

        Returns:
            Redis client instance

        Raises:
            RuntimeError: If Redis client cannot be obtained
        """
        if self._redis_client is not None:
            return self._redis_client

        manager = get_redis_client_manager()
        client = await manager.get_client(self._db_number)
        if client is None:
            raise RuntimeError(
                "Redis client is not available. "
                "LLM cache requires Redis and does not support in-memory fallback."
            )
        return client

    def _generate_cache_key(
        self, prompt: str, model: str | None = None, temperature: float | None = None
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

    def _get_full_key(self, cache_key: str) -> str:
        """
        Get full Redis key with prefix.

        Args:
            cache_key: Base cache key (SHA256 hash)

        Returns:
            Full Redis key with prefix
        """
        return f"{self._key_prefix}{cache_key}"

    async def get(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str | None:
        """
        Get cached LLM response if available and not expired.

        Args:
            prompt: The prompt text
            model: Optional model name
            temperature: Optional temperature setting

        Returns:
            Cached response if found and valid, None otherwise

        Raises:
            RuntimeError: If Redis is not available
        """
        try:
            client = await self._get_client()
            cache_key = self._generate_cache_key(prompt, model, temperature)
            redis_key = self._get_full_key(cache_key)
            cached_value = await client.get(redis_key)

            if cached_value:
                logger.debug(f"Redis cache hit for key: {cache_key[:16]}...")
                return cached_value

            return None

        except Exception as e:
            logger.error(
                f"Redis cache read failed: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to read from Redis cache: {e}. "
                "LLM cache requires Redis and does not support in-memory fallback."
            ) from e

    async def set(
        self,
        prompt: str,
        response: str,
        model: str | None = None,
        temperature: float | None = None,
        ttl: int | None = None,
    ) -> None:
        """
        Cache LLM response in Redis.

        Args:
            prompt: The prompt text
            response: The LLM response to cache
            model: Optional model name
            temperature: Optional temperature setting
            ttl: Optional TTL in seconds. If None, uses default_ttl.

        Raises:
            RuntimeError: If Redis is not available
        """
        try:
            client = await self._get_client()
            cache_key = self._generate_cache_key(prompt, model, temperature)
            redis_key = self._get_full_key(cache_key)
            ttl = ttl if ttl is not None else self._default_ttl

            await client.setex(redis_key, ttl, response)
            logger.debug(f"Cached response in Redis for key: {cache_key[:16]}...")

        except Exception as e:
            logger.error(
                f"Redis cache write failed: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to write to Redis cache: {e}. "
                "LLM cache requires Redis and does not support in-memory fallback."
            ) from e

    async def clear(self) -> None:
        """
        Clear all cached responses from Redis.

        Raises:
            RuntimeError: If Redis is not available
        """
        try:
            client = await self._get_client()
            pattern = f"{self._key_prefix}*"
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
            logger.info(f"Cleared {len(keys)} entries from Redis cache")
        except Exception as e:
            logger.error(
                f"Failed to clear Redis cache: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to clear Redis cache: {e}. "
                "LLM cache requires Redis and does not support in-memory fallback."
            ) from e

    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics from Redis.

        Returns:
            Dictionary with cache statistics

        Raises:
            RuntimeError: If Redis is not available
        """
        stats: dict[str, Any] = {
            "redis_available": False,
            "redis_cache": {
                "total_entries": 0,
            },
            "ttl_seconds": self._default_ttl,
        }

        try:
            client = await self._get_client()
            await client.ping()
            stats["redis_available"] = True

            pattern = f"{self._key_prefix}*"
            keys = await client.keys(pattern)
            stats["redis_cache"]["total_entries"] = len(keys)
        except Exception as e:
            logger.debug(f"Failed to get Redis cache stats: {e}")
            stats["redis_available"] = False

        return stats
