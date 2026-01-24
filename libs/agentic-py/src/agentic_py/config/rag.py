"""
RAG Configuration

Configuration for RAG, vector stores, chunking, and ingestion settings using Pydantic Settings.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    """RAG and vector store configuration."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # RAG Configuration
    rag_enabled: bool = Field(
        default=False,
        description="Enable RAG functionality",
    )
    rag_top_k: int = Field(
        default=3,
        ge=1,
        le=100,
        description="Number of top results to retrieve",
    )
    rag_similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for retrieval (0.0-1.0)",
    )

    # Vector Store Configuration
    vector_store_type: Literal["pgvector", "faiss"] = Field(
        default="pgvector",
        description="Vector store type (pgvector or faiss)",
    )

    # pgvector Configuration
    pgvector_connection_string: str = Field(
        default="postgresql://aura:aura@localhost:5432/aura_db",
        description="PostgreSQL connection string for pgvector (can also use POSTGRES_DB_URI or DATABASE_URL)",
    )
    pgvector_collection: str = Field(
        default="aura_knowledge_base",
        description="pgvector collection name",
    )
    pgvector_table_name: str = Field(
        default="embeddings",
        description="pgvector table name",
    )

    # FAISS Configuration
    faiss_index_path: str = Field(
        default="./faiss_index",
        description="Path to FAISS index file",
    )

    # Chunking Strategy Configuration
    chunking_strategy: Literal["fixed", "recursive", "semantic"] = Field(
        default="recursive",
        description="Chunking strategy (fixed, recursive, or semantic)",
    )
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Chunk size in characters",
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=1000,
        description="Chunk overlap in characters",
    )

    # Evaluation Configuration
    eval_enabled: bool = Field(
        default=False,
        description="Enable evaluation pipeline",
    )
    eval_dataset_path: str = Field(
        default="./eval_dataset.json",
        description="Path to evaluation dataset JSON file",
    )

    # RAG Ingestion Configuration
    rag_max_file_size: int = Field(
        default=10485760,  # 10MB
        ge=1024,  # 1KB minimum
        description="Maximum file size for ingestion in bytes",
    )
    rag_ingestion_batch_size: int = Field(
        default=100,
        ge=1,
        description="Number of documents per ingestion batch",
    )
    rag_allowed_base_dirs: list[str] = Field(
        default_factory=list,
        description="Comma-separated list of allowed base directories (empty = no restriction)",
    )

    @field_validator("pgvector_connection_string", mode="before")
    @classmethod
    def resolve_connection_string(cls, v: str | None) -> str:
        """Resolve connection string from multiple environment variable sources."""
        import os

        if v and v != "postgresql://aura:aura@localhost:5432/aura_db":
            return v

        return (
            os.getenv("PGVECTOR_CONNECTION_STRING")
            or os.getenv("POSTGRES_DB_URI")
            or os.getenv("DATABASE_URL")
            or "postgresql://aura:aura@localhost:5432/aura_db"
        )


# Global instance (lazy-loaded)
_rag_config: RAGConfig | None = None


def get_rag_config() -> RAGConfig:
    """Get RAG configuration instance (singleton)."""
    global _rag_config
    if _rag_config is None:
        _rag_config = RAGConfig()
    return _rag_config


# Backward compatibility: export as module-level constants
_config = get_rag_config()
RAG_ENABLED = _config.rag_enabled
RAG_TOP_K = _config.rag_top_k
RAG_SIMILARITY_THRESHOLD = _config.rag_similarity_threshold
VECTOR_STORE_TYPE = _config.vector_store_type
PGVECTOR_CONNECTION_STRING = _config.pgvector_connection_string
PGVECTOR_COLLECTION = _config.pgvector_collection
PGVECTOR_TABLE_NAME = _config.pgvector_table_name
FAISS_INDEX_PATH = _config.faiss_index_path
CHUNKING_STRATEGY = _config.chunking_strategy
CHUNK_SIZE = _config.chunk_size
CHUNK_OVERLAP = _config.chunk_overlap
EVAL_ENABLED = _config.eval_enabled
EVAL_DATASET_PATH = _config.eval_dataset_path
RAG_MAX_FILE_SIZE = _config.rag_max_file_size
RAG_INGESTION_BATCH_SIZE = _config.rag_ingestion_batch_size
RAG_ALLOWED_BASE_DIRS = _config.rag_allowed_base_dirs
