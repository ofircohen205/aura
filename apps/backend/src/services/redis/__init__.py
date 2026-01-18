"""
Redis Service

Provides Redis client for authentication and other services.
"""

from services.redis.client import (
    REDIS_RATE_LIMIT_DB,
    get_redis_client,
    test_redis_connection,
)

__all__: list[str] = ["get_redis_client", "test_redis_connection", "REDIS_RATE_LIMIT_DB"]
