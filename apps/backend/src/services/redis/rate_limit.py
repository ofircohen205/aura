"""
Redis Rate Limiting Service

Provides rate limiting functionality using Redis token bucket algorithm.
"""

import time

from loguru import logger

from core.config import get_settings
from services.redis.client import get_redis_client_manager

settings = get_settings()


class RateLimitService:
    """
    Rate limiting service using Redis token bucket algorithm.

    Provides methods to refill and consume tokens for rate limiting.
    """

    def __init__(self, redis_client_manager=None):
        """
        Initialize rate limiting service.

        Args:
            redis_client_manager: Optional RedisClient instance. If None, uses get_redis_client_manager().
        """
        self._manager = redis_client_manager or get_redis_client_manager()
        self._key_prefix = "rate_limit:"

    def _get_key(self, client_id: str, endpoint: str) -> str:
        """
        Get Redis key for rate limit bucket.

        Args:
            client_id: Client identifier
            endpoint: Endpoint path

        Returns:
            Redis key string
        """
        return f"{self._key_prefix}{client_id}:{endpoint}"

    async def refill_tokens(
        self,
        client_id: str,
        endpoint: str,
        max_tokens: int,
        window: int,
        redis_enabled: bool | None = None,
    ) -> float:
        """
        Refill token bucket using Redis (distributed token bucket algorithm).

        Args:
            client_id: Client identifier
            endpoint: Endpoint path
            max_tokens: Maximum tokens in bucket
            window: Time window in seconds
            redis_enabled: Whether Redis is enabled. If None, uses settings.

        Returns:
            Current number of tokens after refill
        """
        redis_enabled = (
            redis_enabled if redis_enabled is not None else settings.rate_limit_redis_enabled
        )

        if not redis_enabled:
            return 0.0

        client = await self._manager.get_client(settings.redis_rate_limit_db)
        if client is None:
            return 0.0

        try:
            key = self._get_key(client_id, endpoint)
            current_time = time.time()

            pipe = client.pipeline()
            pipe.hgetall(key)
            results = await pipe.execute()

            bucket_data = results[0] if results else {}

            if not bucket_data:
                tokens = float(max_tokens)
                last_refill = current_time
            else:
                tokens = float(bucket_data.get("tokens", max_tokens))
                last_refill = float(bucket_data.get("last_refill", current_time))

            elapsed = current_time - last_refill

            refill_rate = max_tokens / window
            tokens_to_add = elapsed * refill_rate
            new_tokens = min(tokens + tokens_to_add, max_tokens)

            pipe = client.pipeline()
            pipe.hset(key, mapping={"tokens": str(new_tokens), "last_refill": str(current_time)})
            pipe.expire(key, window * 2)
            await pipe.execute()

            return new_tokens

        except Exception as e:
            logger.warning(f"Redis rate limit refill failed: {e}", exc_info=True)
            return 0.0

    async def consume_token(
        self,
        client_id: str,
        endpoint: str,
        max_tokens: int,
        window: int,
        redis_enabled: bool | None = None,
    ) -> bool:
        """
        Consume a token from the Redis bucket.

        Args:
            client_id: Client identifier
            endpoint: Endpoint path
            max_tokens: Maximum tokens in bucket
            window: Time window in seconds
            redis_enabled: Whether Redis is enabled. If None, uses settings.

        Returns:
            True if token was consumed, False if bucket is empty
        """
        redis_enabled = (
            redis_enabled if redis_enabled is not None else settings.rate_limit_redis_enabled
        )

        tokens = await self.refill_tokens(client_id, endpoint, max_tokens, window, redis_enabled)

        if tokens < 1.0:
            return False

        if not redis_enabled:
            return False

        client = await self._manager.get_client(settings.redis_rate_limit_db)
        if client is None:
            return False

        try:
            key = self._get_key(client_id, endpoint)
            current_time = time.time()

            pipe = client.pipeline()
            pipe.hset(key, "tokens", str(tokens - 1.0))
            pipe.hset(key, "last_refill", str(current_time))
            pipe.expire(key, window * 2)
            await pipe.execute()

            return True
        except Exception as e:
            logger.warning(f"Redis token consumption failed: {e}", exc_info=True)
            return False


_rate_limit_service = RateLimitService()


def get_rate_limit_service() -> RateLimitService:
    """
    Get the global RateLimitService instance.

    Returns:
        Global RateLimitService instance
    """
    return _rate_limit_service
