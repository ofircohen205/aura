"""
Configuration Management

Centralized configuration using Pydantic Settings with environment-based overrides.
Supports .env.local, .env.staging, and .env.production files.
"""

import json
import os
from enum import Enum
from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

    def get_env_file(self) -> str:
        """Get the environment file path for this environment."""
        return f".env.{self.value}"

    def get_env_vars(self) -> dict[str, Any]:
        """
        Load environment variables from .env file if it exists.

        Returns:
            dict: Environment variables from file, or empty dict if file doesn't exist
        """
        env_file = self.get_env_file()
        if not os.path.exists(env_file):
            return {}

        env_vars: dict[str, Any] = {}
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        env_vars[key.strip()] = value
        except Exception:
            return {}

        return env_vars


def _get_default_cors_origins() -> list[str]:
    """
    Get default CORS origins (will be overridden by model_validator if needed).

    Returns:
        List of allowed CORS origins
    """
    return []


def _get_default_cors_credentials() -> bool:
    """
    Get default CORS credentials setting (will be overridden by model_validator if needed).

    Returns:
        Whether to allow credentials
    """
    return False


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Field(
        default=Environment.LOCAL,  # type: ignore[arg-type]
        description="Application environment",
    )

    # Database Configuration
    postgres_db_uri: str = Field(
        default="postgresql+asyncpg://aura:aura@localhost:5432/aura_db",
        description="PostgreSQL database URI for LangGraph checkpointer. Must be set via environment variable in production.",
    )
    postgres_pool_max_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum connection pool size",
    )
    postgres_pool_min_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Minimum connection pool size",
    )

    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: _get_default_cors_origins(),
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default_factory=lambda: _get_default_cors_credentials(),
        description="Allow credentials in CORS requests",
    )
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed HTTP methods for CORS",
    )
    cors_allow_headers: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed headers for CORS",
    )

    # API Configuration
    api_title: str = Field(
        default="Aura Backend",
        description="API title for OpenAPI documentation",
    )
    api_version: str = Field(
        default="0.1.0",
        description="API version",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["json", "text"] | None = Field(
        default=None,
        description="Log format (json for production, text for local). Auto-set based on environment if None.",
    )

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="test-secret-key-for-jwt-tokens-minimum-32-chars-for-testing-only",
        description="Secret key for JWT signing. Must be set via environment variable in production.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm (e.g., HS256, RS256)",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="Access token expiration time in minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        description="Refresh token expiration time in days",
    )

    # CSRF Protection Configuration
    csrf_protection_enabled: bool = Field(
        default=True,
        description="Enable CSRF protection middleware",
    )

    # Rate Limiting Configuration
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting middleware",
    )
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Default number of requests per time window",
    )
    rate_limit_window: int = Field(
        default=60,
        ge=1,
        description="Default time window in seconds",
    )
    rate_limit_redis_enabled: bool = Field(
        default=True,
        description="Enable Redis for rate limiting (required for distributed rate limiting)",
    )
    rate_limit_endpoints: dict[str, dict[str, int]] = Field(
        default_factory=lambda: {
            "/api/v1/workflows/struggle": {"requests": 50, "window": 60},
            "/api/v1/workflows/audit": {"requests": 30, "window": 60},
            "/api/v1/workflows": {"requests": 100, "window": 60},
        },
        description="Per-endpoint rate limit configuration (requests per window)",
    )

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_auth_db: int = Field(
        default=2,
        description="Redis authentication database number",
    )
    redis_rate_limit_db: int = Field(
        default=1,
        description="Redis rate limit database number",
    )
    redis_llm_cache_db: int = Field(
        default=0,
        description="Redis LLM cache database number",
    )
    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis for distributed caching and rate limiting",
    )

    @model_validator(mode="after")
    def set_defaults_based_on_environment(self) -> "Settings":
        """
        Set default values based on environment after initialization.

        This runs after all fields are set, allowing us to use the environment field.
        Note: We can't perfectly detect if a value was explicitly set vs default,
        so we use heuristics (empty list for CORS origins, False for credentials).
        """
        env_value = self.environment.value

        # Set CORS defaults based on environment
        # If cors_allow_origins is empty (default), set based on environment
        if not self.cors_allow_origins and env_value == "local":
            self.cors_allow_origins = ["http://localhost:3000"]

        # Set CORS credentials based on environment
        # If False (default) and local, set to True
        if not self.cors_allow_credentials and env_value == "local":
            self.cors_allow_credentials = True

        # Set log format based on environment if not explicitly set
        if self.log_format is None:
            self.log_format = "text" if env_value == "local" else "json"

        return self

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: str | list[str]) -> list[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [method.strip() for method in v.split(",") if method.strip()]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: str | list[str]) -> list[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(",") if header.strip()]
        return v

    @field_validator("rate_limit_endpoints", mode="before")
    @classmethod
    def parse_rate_limit_endpoints(
        cls, v: str | dict[str, dict[str, int]]
    ) -> dict[str, dict[str, int]]:
        r"""
        Parse rate limit endpoints from JSON string or dict.

        Environment variable format: JSON string like:
        '{"\/api\/v1\/workflows\/struggle": {"requests": 50, "window": 60}}'
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format for rate_limit_endpoints: {e}") from e
        return v

    @model_validator(mode="after")
    def validate_cors_origins_environment(self) -> "Settings":
        """Validate CORS origins against environment."""
        if "*" in self.cors_allow_origins and self.environment.value != "local":
            raise ValueError("Cannot use '*' origin in non-local environments")
        return self

    def get_env_file(self) -> str | None:
        """Get the appropriate .env file based on environment."""
        env_files = {
            "local": ".env.local",
            "staging": ".env.staging",
            "production": ".env.production",
        }
        return env_files.get(self.environment.value)


@lru_cache
def get_settings() -> Settings:
    """
    Get application settings (cached).

    Loads settings from environment variables with fallback to defaults.
    Environment-specific .env files can be used for local overrides.

    Returns:
        Settings: Application configuration instance
    """
    env_str = os.getenv("ENVIRONMENT") or os.getenv("ENV", "local") or "local"
    try:
        env = Environment(env_str.lower())
    except ValueError:
        env = Environment.LOCAL

    env_file: str | None = env.get_env_file()
    env_file = env_file if env_file and os.path.exists(env_file) else None

    return Settings(
        _env_file=env_file,  # type: ignore[call-arg]
        environment=env,  # type: ignore[arg-type]
    )


settings = get_settings()
