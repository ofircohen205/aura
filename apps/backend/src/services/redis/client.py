"""
Redis Client

Provides Redis client for authentication and other services.
Uses connection pooling and handles errors gracefully.
"""

import contextlib
from typing import Any

from loguru import logger

from core.config import get_settings


class RedisClient:
    """
    Redis client manager for managing multiple database connections.

    Manages Redis connections with connection pooling, one client per database.
    Provides methods to get clients for specific databases and manage connections.
    """

    def __init__(self, settings=None):
        """
        Initialize Redis client manager.

        Args:
            settings: Optional Settings instance. If None, uses get_settings().
        """
        self._settings = settings or get_settings()
        self._redis_clients: dict[int, Any] = {}
        self._redis_available = False

    @property
    def redis_url(self) -> str:
        """Get Redis URL from settings."""
        return self._settings.redis_url

    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is enabled from settings."""
        return self._settings.redis_enabled

    @property
    def redis_auth_db(self) -> int:
        """Get Redis auth database number from settings."""
        return self._settings.redis_auth_db

    @property
    def redis_rate_limit_db(self) -> int:
        """Get Redis rate limit database number from settings."""
        return self._settings.redis_rate_limit_db

    def _get_redis_url(self, db_number: int) -> str:
        """
        Get Redis URL for a specific database.

        Args:
            db_number: Database number to use

        Returns:
            Redis URL string with appropriate database
        """
        if "/" in self.redis_url and self.redis_url.split("/")[-1].isdigit():
            base_url = self.redis_url.rsplit("/", 1)[0]
            return f"{base_url}/{db_number}"
        return f"{self.redis_url}/{db_number}"

    async def get_client(self, db_number: int | None = None) -> Any | None:
        """
        Get or create Redis client with connection pooling.

        Args:
            db_number: Database number to use. If None, uses redis_auth_db (default: 2)

        Returns:
            Redis client instance or None if Redis is unavailable
        """
        if not self.redis_enabled:
            return None

        if db_number is None:
            db_number = self.redis_auth_db

        if db_number in self._redis_clients:
            return self._redis_clients[db_number]

        try:
            import redis.asyncio as redis  # type: ignore[import-untyped]
            from redis.asyncio.connection import ConnectionPool  # type: ignore[import-untyped]

            redis_url = self._get_redis_url(db_number)
            pool: ConnectionPool = ConnectionPool.from_url(
                redis_url,
                max_connections=10,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )

            client = redis.Redis(connection_pool=pool)
            self._redis_clients[db_number] = client
            self._redis_available = True

            try:
                await client.ping()
                logger.info(
                    "Redis client initialized and connected",
                    extra={
                        "redis_url": redis_url.split("@")[-1],
                        "db": db_number,
                        "status": "connected",
                    },
                )
            except Exception as e:
                logger.warning(
                    "Redis client initialized but connection test failed",
                    extra={
                        "redis_url": redis_url.split("@")[-1],
                        "db": db_number,
                        "status": "connection_failed",
                        "error": str(e),
                    },
                )

            return client

        except ImportError:
            logger.warning("redis package not installed, Redis features disabled")
            self._redis_available = False
            return None
        except Exception as e:
            logger.warning(
                f"Failed to initialize Redis client for database {db_number}, Redis features disabled: {e}",
                exc_info=True,
            )
            self._redis_available = False
            return None

    async def close_all(self) -> None:
        """
        Close all Redis client connections.

        This should be called during application shutdown or test cleanup
        to properly close connections and avoid event loop issues.
        """
        for db_number, client in list(self._redis_clients.items()):
            try:
                await client.aclose()
                logger.debug(f"Redis client closed for database {db_number}")
            except Exception as e:
                error_msg = str(e).lower()
                if any(
                    phrase in error_msg
                    for phrase in [
                        "event loop is closed",
                        "no running event loop",
                        "loop is closed",
                    ]
                ):
                    logger.debug(
                        f"Redis client for database {db_number} could not be closed (event loop closed)"
                    )
                else:
                    logger.warning(
                        f"Error closing Redis client for database {db_number}: {e}",
                        exc_info=True,
                    )

        self._redis_clients.clear()
        self._redis_available = False

    async def test_connection(self, db_number: int | None = None) -> bool:
        """
        Test Redis connection availability.

        Args:
            db_number: Database number to test. If None, uses redis_auth_db (default: 2)

        Returns:
            True if Redis is available and connected, False otherwise
        """
        if not self.redis_enabled:
            logger.debug("Redis connection test skipped: Redis disabled")
            return False

        if db_number is None:
            db_number = self.redis_auth_db

        logger.debug(
            "Testing Redis connection",
            extra={"db": db_number},
        )

        try:
            client = await self.get_client(db_number)
            if client is None:
                logger.debug(
                    "Redis connection test failed: client is None",
                    extra={"db": db_number},
                )
                return False

            await client.ping()
            logger.debug(
                "Redis connection test successful",
                extra={"db": db_number},
            )
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if any(
                phrase in error_msg
                for phrase in [
                    "event loop is closed",
                    "no running event loop",
                    "loop is closed",
                    "got future attached to a different loop",
                ]
            ):
                logger.debug(
                    "Redis connection test skipped (event loop issue)",
                    extra={"db": db_number, "error": str(e)},
                )
                if db_number in self._redis_clients:
                    with contextlib.suppress(Exception):
                        await self._redis_clients[db_number].aclose()
                    del self._redis_clients[db_number]
            else:
                logger.warning(
                    "Redis connection test failed",
                    extra={"db": db_number, "error": str(e), "error_type": type(e).__name__},
                )
            return False

    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._redis_available and self.redis_enabled


_redis_client_manager = RedisClient()


def get_redis_client_manager() -> RedisClient:
    """
    Get the global RedisClient instance.

    Returns:
        Global RedisClient instance

    Example:
        >>> manager = get_redis_client_manager()
        >>> client = await manager.get_client(manager.redis_auth_db)
    """
    return _redis_client_manager
