"""
Authentication Service Cache

Provides caching for frequently accessed user data to improve performance.
Uses Redis for distributed caching.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger

from services.redis import REDIS_AUTH_DB, get_redis_client

if TYPE_CHECKING:
    from redis.asyncio import Redis  # type: ignore[import-untyped]

# Cache TTL in seconds
USER_CACHE_TTL = 300  # 5 minutes


async def get_cached_user(user_id: UUID) -> dict | None:
    """
    Get cached user data from Redis.

    Args:
        user_id: User ID to retrieve

    Returns:
        Cached user data dict or None if not cached
    """
    redis_client: Redis[str] | None = await get_redis_client(REDIS_AUTH_DB)
    if not redis_client:
        return None

    try:
        cache_key = f"user:{user_id}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            import json

            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Failed to get cached user: {e}")
        return None

    return None


async def cache_user(user_id: UUID, user_data: dict) -> None:
    """
    Cache user data in Redis.

    Args:
        user_id: User ID
        user_data: User data dictionary to cache
    """
    redis_client: Redis[str] | None = await get_redis_client(REDIS_AUTH_DB)
    if not redis_client:
        return

    try:
        import json

        cache_key = f"user:{user_id}"
        await redis_client.setex(
            cache_key,
            USER_CACHE_TTL,
            json.dumps(user_data, default=str),
        )
        logger.debug(f"Cached user data for user_id: {user_id}")
    except Exception as e:
        logger.warning(f"Failed to cache user: {e}")


async def invalidate_user_cache(user_id: UUID) -> None:
    """
    Invalidate cached user data.

    Args:
        user_id: User ID to invalidate
    """
    redis_client: Redis[str] | None = await get_redis_client(REDIS_AUTH_DB)
    if not redis_client:
        return

    try:
        cache_key = f"user:{user_id}"
        await redis_client.delete(cache_key)
        logger.debug(f"Invalidated cache for user_id: {user_id}")
    except Exception as e:
        logger.warning(f"Failed to invalidate user cache: {e}")
