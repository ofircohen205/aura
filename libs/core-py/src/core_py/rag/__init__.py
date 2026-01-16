"""
RAG Module

Retrieval-Augmented Generation service for querying knowledge base.
"""

# Export ingestion utilities
from core_py.rag.chunking import chunk_text, get_text_splitter
from core_py.rag.dependency_injection import (
    get_rag_service_injected,
    get_rag_service_provider,
    set_rag_service_provider,
)
from core_py.rag.exceptions import (
    RAGConfigurationError,
    RAGError,
    RAGFileError,
    RAGIngestionError,
    RAGPathError,
    RAGValidationError,
)
from core_py.rag.ingestion import discover_files, ingest_directory, ingest_document
from core_py.rag.loaders import (
    load_document,
    load_markdown,
    load_python,
    load_text,
    load_typescript,
)
from core_py.rag.service import RagService, get_rag_service
from core_py.rag.utils import (
    read_file_async,
    validate_file_size,
    validate_path,
)

__all__ = [
    "RagService",
    "get_rag_service",
    "get_rag_service_injected",
    "get_rag_service_provider",
    "set_rag_service_provider",
    # Chunking
    "chunk_text",
    "get_text_splitter",
    # Loaders
    "load_document",
    "load_markdown",
    "load_python",
    "load_text",
    "load_typescript",
    # Ingestion
    "discover_files",
    "ingest_document",
    "ingest_directory",
    # Exceptions
    "RAGError",
    "RAGConfigurationError",
    "RAGFileError",
    "RAGIngestionError",
    "RAGPathError",
    "RAGValidationError",
    # Utils
    "read_file_async",
    "validate_file_size",
    "validate_path",
]
