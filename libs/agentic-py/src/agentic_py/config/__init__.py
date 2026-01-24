"""
Configuration Module

Centralized configuration for all agentic-py components using Pydantic Settings.
Configuration is split by domain for better organization.

Each config domain has:
- A Pydantic Settings model (e.g., LLMConfig)
- A getter function (e.g., get_llm_config())
- Backward-compatible module-level constants
"""

# Import config classes
# Re-export all config constants for backward compatibility
from agentic_py.config.cache import (
    LLM_CACHE_ENABLED,
    LLM_CACHE_TTL,
    REDIS_CONNECTION_POOL_SIZE,
    REDIS_ENABLED,
    REDIS_KEY_PREFIX,
    REDIS_SOCKET_CONNECT_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
    REDIS_URL,
    CacheConfig,
    get_cache_config,
)
from agentic_py.config.llm import (
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    LLM_BATCH_DELAY,
    LLM_BATCH_SIZE,
    LLM_ENABLED,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLMConfig,
    get_llm_config,
)
from agentic_py.config.rag import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKING_STRATEGY,
    EVAL_DATASET_PATH,
    EVAL_ENABLED,
    FAISS_INDEX_PATH,
    PGVECTOR_COLLECTION,
    PGVECTOR_CONNECTION_STRING,
    PGVECTOR_TABLE_NAME,
    RAG_ALLOWED_BASE_DIRS,
    RAG_ENABLED,
    RAG_INGESTION_BATCH_SIZE,
    RAG_MAX_FILE_SIZE,
    RAG_SIMILARITY_THRESHOLD,
    RAG_TOP_K,
    VECTOR_STORE_TYPE,
    RAGConfig,
    get_rag_config,
)
from agentic_py.config.workflows import (
    AUDIT_FUNCTION_LENGTH_THRESHOLD,
    STRUGGLE_THRESHOLD_EDIT_FREQUENCY,
    STRUGGLE_THRESHOLD_ERROR_COUNT,
    WorkflowConfig,
    get_workflow_config,
)

__all__ = [
    # Config Classes
    "LLMConfig",
    "get_llm_config",
    "RAGConfig",
    "get_rag_config",
    "WorkflowConfig",
    "get_workflow_config",
    "CacheConfig",
    "get_cache_config",
    # LLM Config Constants
    "LLM_MODEL",
    "LLM_TEMPERATURE",
    "LLM_ENABLED",
    "EMBEDDING_MODEL",
    "EMBEDDING_PROVIDER",
    "LLM_BATCH_SIZE",
    "LLM_BATCH_DELAY",
    # RAG Config Constants
    "RAG_ENABLED",
    "RAG_TOP_K",
    "RAG_SIMILARITY_THRESHOLD",
    "CHUNKING_STRATEGY",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "VECTOR_STORE_TYPE",
    "PGVECTOR_CONNECTION_STRING",
    "PGVECTOR_COLLECTION",
    "PGVECTOR_TABLE_NAME",
    "FAISS_INDEX_PATH",
    "RAG_MAX_FILE_SIZE",
    "RAG_INGESTION_BATCH_SIZE",
    "RAG_ALLOWED_BASE_DIRS",
    "EVAL_ENABLED",
    "EVAL_DATASET_PATH",
    # Workflow Config Constants
    "STRUGGLE_THRESHOLD_EDIT_FREQUENCY",
    "STRUGGLE_THRESHOLD_ERROR_COUNT",
    "AUDIT_FUNCTION_LENGTH_THRESHOLD",
    # Cache Config Constants
    "LLM_CACHE_ENABLED",
    "LLM_CACHE_TTL",
    "REDIS_ENABLED",
    "REDIS_URL",
    "REDIS_KEY_PREFIX",
    "REDIS_CONNECTION_POOL_SIZE",
    "REDIS_SOCKET_TIMEOUT",
    "REDIS_SOCKET_CONNECT_TIMEOUT",
]
