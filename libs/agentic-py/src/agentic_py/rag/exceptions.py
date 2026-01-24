"""
RAG Pipeline Exceptions

Custom exception classes for the RAG pipeline to provide clear error handling.
"""


class RAGError(Exception):
    """Base exception for all RAG pipeline errors."""

    pass


class RAGConfigurationError(RAGError):
    """Raised when RAG configuration is invalid."""

    pass


class RAGIngestionError(RAGError):
    """Raised when document ingestion fails."""

    pass


class RAGValidationError(RAGError):
    """Raised when input validation fails."""

    pass


class RAGPathError(RAGError):
    """Raised when path validation fails (e.g., path traversal attempt)."""

    pass


class RAGFileError(RAGError):
    """Raised when file operations fail."""

    pass
