"""
Cache Configuration

Configuration for LLM caching and Redis settings using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    """Cache configuration for LLM responses and Redis."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Caching Configuration
    llm_cache_enabled: bool = Field(
        default=True,
        description="Enable LLM response caching",
    )
    llm_cache_ttl: int = Field(
        default=3600,  # 1 hour
        ge=1,
        description="Cache TTL in seconds",
    )

    # Redis Configuration
    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis for distributed caching",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_key_prefix: str = Field(
        default="aura:llm:cache:",
        description="Prefix for Redis cache keys",
    )
    redis_connection_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Redis connection pool size",
    )
    redis_socket_timeout: float = Field(
        default=5.0,
        ge=0.1,
        description="Redis socket timeout in seconds",
    )
    redis_socket_connect_timeout: float = Field(
        default=5.0,
        ge=0.1,
        description="Redis socket connect timeout in seconds",
    )


# Global instance (lazy-loaded)
_cache_config: CacheConfig | None = None


def get_cache_config() -> CacheConfig:
    """Get cache configuration instance (singleton)."""
    global _cache_config
    if _cache_config is None:
        _cache_config = CacheConfig()
    return _cache_config


# Backward compatibility: export as module-level constants
_config = get_cache_config()
LLM_CACHE_ENABLED = _config.llm_cache_enabled
LLM_CACHE_TTL = _config.llm_cache_ttl
REDIS_ENABLED = _config.redis_enabled
REDIS_URL = _config.redis_url
REDIS_KEY_PREFIX = _config.redis_key_prefix
REDIS_CONNECTION_POOL_SIZE = _config.redis_connection_pool_size
REDIS_SOCKET_TIMEOUT = _config.redis_socket_timeout
REDIS_SOCKET_CONNECT_TIMEOUT = _config.redis_socket_connect_timeout
