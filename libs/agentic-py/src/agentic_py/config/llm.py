"""
LLM Configuration

Configuration for LLM models, embeddings, and batching settings using Pydantic Settings.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """LLM and embedding model configuration."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # Model Configuration
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="LLM model name (e.g., gpt-4o-mini, gpt-4o)",
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature (0.0-2.0)",
    )
    llm_enabled: bool = Field(
        default=False,
        description="Enable LLM functionality",
    )

    # Embedding Model Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name",
    )
    embedding_provider: Literal["openai", "local"] = Field(
        default="openai",
        description="Embedding provider (openai or local)",
    )

    # LLM Batching Configuration
    llm_batch_size: int = Field(
        default=5,
        ge=1,
        description="Number of prompts per batch",
    )
    llm_batch_delay: float = Field(
        default=0.1,
        ge=0.0,
        description="Delay between batches in seconds",
    )


# Global instance (lazy-loaded)
_llm_config: LLMConfig | None = None


def get_llm_config() -> LLMConfig:
    """Get LLM configuration instance (singleton)."""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config


# Backward compatibility: export as module-level constants
_config = get_llm_config()
LLM_MODEL = _config.llm_model
LLM_TEMPERATURE = _config.llm_temperature
LLM_ENABLED = _config.llm_enabled
EMBEDDING_MODEL = _config.embedding_model
EMBEDDING_PROVIDER = _config.embedding_provider
LLM_BATCH_SIZE = _config.llm_batch_size
LLM_BATCH_DELAY = _config.llm_batch_delay
