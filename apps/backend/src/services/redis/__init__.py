"""
Redis Service

Provides Redis client for authentication and other services.
"""

from services.redis.client import (
    REDIS_AUTH_DB,
    REDIS_RATE_LIMIT_DB,
    close_redis_clients,
    get_redis_client,
    test_redis_connection,
)

__all__: list[str] = [
    "get_redis_client",
    "test_redis_connection",
    "close_redis_clients",
    "REDIS_AUTH_DB",
    "REDIS_RATE_LIMIT_DB",
]
