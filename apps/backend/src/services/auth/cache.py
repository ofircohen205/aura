"""
Authentication Service Cache

Provides caching for frequently accessed user data to improve performance.
Uses Redis for distributed caching.
"""

import time
from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger
from pydantic import BaseModel

from core.config import get_settings
from services.redis import get_redis_client_manager

settings = get_settings()

if TYPE_CHECKING:
    from redis.asyncio import Redis  # type: ignore[import-untyped]

USER_CACHE_TTL = 300  # 5 minutes


class UserCache(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    roles: list[str]


async def get_cached_user(user_id: UUID) -> UserCache | None:
    """
    Get cached user data from Redis.

    Args:
        user_id: User ID to retrieve

    Returns:
        Cached user cache object or None if not cached
    """
    start_time = time.time()
    manager = get_redis_client_manager()
    redis_client: Redis[str] | None = await manager.get_client(settings.redis_auth_db)
    if not redis_client:
        logger.debug(
            "Cache get skipped: Redis client unavailable",
            extra={"user_id": str(user_id), "operation": "get_cached_user"},
        )
        return None

    try:
        cache_key = f"user:{user_id}"
        logger.debug(
            "Getting cached user from Redis",
            extra={"user_id": str(user_id), "cache_key": cache_key},
        )

        cached_data = await redis_client.get(cache_key)
        duration = time.time() - start_time

        if cached_data:
            user_cache = UserCache.model_validate_json(cached_data)
            logger.debug(
                "Cache hit: user data retrieved",
                extra={
                    "user_id": str(user_id),
                    "cache_key": cache_key,
                    "duration_ms": duration * 1000,
                    "operation": "get_cached_user",
                },
            )
            return user_cache
        else:
            logger.debug(
                "Cache miss: user data not found",
                extra={
                    "user_id": str(user_id),
                    "cache_key": cache_key,
                    "duration_ms": duration * 1000,
                    "operation": "get_cached_user",
                },
            )
    except Exception as e:
        duration = time.time() - start_time
        logger.warning(
            "Failed to get cached user",
            extra={
                "user_id": str(user_id),
                "duration_ms": duration * 1000,
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "get_cached_user",
            },
        )
        return None

    return None


async def cache_user(user_id: UUID, user_cache: UserCache) -> None:
    """
    Cache user data in Redis.

    Args:
        user_id: User ID
        user_cache: User cache object to cache
    """
    start_time = time.time()
    manager = get_redis_client_manager()
    redis_client: Redis[str] | None = await manager.get_client(settings.redis_auth_db)
    if not redis_client:
        logger.debug(
            "Cache set skipped: Redis client unavailable",
            extra={"user_id": str(user_id), "operation": "cache_user"},
        )
        return

    try:
        cache_key = f"user:{user_id}"
        logger.debug(
            "Caching user data in Redis",
            extra={
                "user_id": str(user_id),
                "cache_key": cache_key,
                "ttl": USER_CACHE_TTL,
                "operation": "cache_user",
            },
        )

        await redis_client.setex(
            cache_key,
            USER_CACHE_TTL,
            user_cache.model_dump_json(),
        )

        duration = time.time() - start_time
        logger.debug(
            "User data cached successfully",
            extra={
                "user_id": str(user_id),
                "cache_key": cache_key,
                "ttl": USER_CACHE_TTL,
                "duration_ms": duration * 1000,
                "operation": "cache_user",
            },
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.warning(
            "Failed to cache user",
            extra={
                "user_id": str(user_id),
                "duration_ms": duration * 1000,
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "cache_user",
            },
        )


async def invalidate_user_cache(user_id: UUID) -> None:
    """
    Invalidate cached user data.

    Args:
        user_id: User ID to invalidate
    """
    start_time = time.time()
    manager = get_redis_client_manager()
    redis_client: Redis[str] | None = await manager.get_client(settings.redis_auth_db)
    if not redis_client:
        logger.debug(
            "Cache invalidation skipped: Redis client unavailable",
            extra={"user_id": str(user_id), "operation": "invalidate_user_cache"},
        )
        return

    try:
        cache_key = f"user:{user_id}"
        logger.debug(
            "Invalidating user cache",
            extra={
                "user_id": str(user_id),
                "cache_key": cache_key,
                "operation": "invalidate_user_cache",
            },
        )

        deleted = await redis_client.delete(cache_key)
        duration = time.time() - start_time

        logger.debug(
            "User cache invalidated",
            extra={
                "user_id": str(user_id),
                "cache_key": cache_key,
                "deleted": bool(deleted),
                "duration_ms": duration * 1000,
                "operation": "invalidate_user_cache",
            },
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.warning(
            "Failed to invalidate user cache",
            extra={
                "user_id": str(user_id),
                "duration_ms": duration * 1000,
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "invalidate_user_cache",
            },
        )
