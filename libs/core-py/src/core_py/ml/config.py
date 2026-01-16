"""
ML Configuration

Configuration for ML models, embeddings, and evaluation settings.
"""

import os
from typing import Literal, cast

# Model Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"

# Embedding Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
_embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
EMBEDDING_PROVIDER: Literal["openai", "local"] = cast(
    Literal["openai", "local"],
    _embedding_provider if _embedding_provider in ("openai", "local") else "openai",
)

# RAG Configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() == "true"
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))

# Vector Store Configuration
_vector_store_type = os.getenv("VECTOR_STORE_TYPE", "pgvector").lower()
VECTOR_STORE_TYPE: Literal["pgvector", "faiss"] = cast(
    Literal["pgvector", "faiss"],
    _vector_store_type if _vector_store_type in ("pgvector", "faiss") else "pgvector",
)

# pgvector Configuration (PostgreSQL extension)
PGVECTOR_CONNECTION_STRING = os.getenv(
    "PGVECTOR_CONNECTION_STRING",
    os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aura"),
)
PGVECTOR_COLLECTION = os.getenv("PGVECTOR_COLLECTION", "aura_knowledge_base")
PGVECTOR_TABLE_NAME = os.getenv("PGVECTOR_TABLE_NAME", "embeddings")

# FAISS Configuration (for local development/testing)
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")

# Chunking Strategy Configuration
_chunking_strategy = os.getenv("CHUNKING_STRATEGY", "recursive").lower()
CHUNKING_STRATEGY: Literal["fixed", "recursive", "semantic"] = cast(
    Literal["fixed", "recursive", "semantic"],
    _chunking_strategy if _chunking_strategy in ("fixed", "recursive", "semantic") else "recursive",
)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Evaluation Configuration
EVAL_ENABLED = os.getenv("EVAL_ENABLED", "false").lower() == "true"
EVAL_DATASET_PATH = os.getenv("EVAL_DATASET_PATH", "./eval_dataset.json")

# Struggle Detection Configuration
STRUGGLE_THRESHOLD_EDIT_FREQUENCY = float(os.getenv("STRUGGLE_THRESHOLD_EDIT_FREQUENCY", "10.0"))
STRUGGLE_THRESHOLD_ERROR_COUNT = int(os.getenv("STRUGGLE_THRESHOLD_ERROR_COUNT", "2"))

# Code Audit Configuration
AUDIT_FUNCTION_LENGTH_THRESHOLD = int(os.getenv("AUDIT_FUNCTION_LENGTH_THRESHOLD", "50"))

# LLM Caching Configuration
LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
LLM_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hour default
LLM_CACHE_MAX_SIZE = int(
    os.getenv("LLM_CACHE_MAX_SIZE", "1000")
)  # Max cached items (for in-memory fallback)

# Redis Configuration (for distributed caching)
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "aura:llm:cache:")
REDIS_CONNECTION_POOL_SIZE = int(os.getenv("REDIS_CONNECTION_POOL_SIZE", "10"))
REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0"))
REDIS_SOCKET_CONNECT_TIMEOUT = float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0"))

# LLM Batching Configuration
LLM_BATCH_SIZE = int(os.getenv("LLM_BATCH_SIZE", "5"))  # Number of prompts per batch
LLM_BATCH_DELAY = float(os.getenv("LLM_BATCH_DELAY", "0.1"))  # Delay between batches (seconds)

# RAG Ingestion Configuration
RAG_MAX_FILE_SIZE = int(os.getenv("RAG_MAX_FILE_SIZE", "10485760"))  # 10MB default
RAG_INGESTION_BATCH_SIZE = int(os.getenv("RAG_INGESTION_BATCH_SIZE", "100"))  # Documents per batch
_rag_allowed_dirs = os.getenv("RAG_ALLOWED_BASE_DIRS", "").strip()
RAG_ALLOWED_BASE_DIRS = (
    [d.strip() for d in _rag_allowed_dirs.split(",") if d.strip()] if _rag_allowed_dirs else []
)  # Comma-separated list of allowed base directories (empty = no restriction)
