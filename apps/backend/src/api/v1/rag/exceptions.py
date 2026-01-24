"""
RAG API Exception Handlers

Exception handlers for RAG service exceptions.
"""

from fastapi import FastAPI, Request
from loguru import logger

from api.exceptions import BaseApplicationException, create_error_response


class RAGServiceUnavailableError(BaseApplicationException):
    """Raised when RAG service is not available."""

    def __init__(self, message: str = "RAG service is not available", details: dict | None = None):
        from fastapi import status

        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {},
        )


class RAGQueryError(BaseApplicationException):
    """Raised when a RAG query fails."""

    def __init__(self, message: str = "RAG query failed", details: dict | None = None):
        from fastapi import status

        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details or {},
        )


class RAGStatsError(BaseApplicationException):
    """Raised when RAG stats retrieval fails."""

    def __init__(self, message: str = "Failed to get RAG stats", details: dict | None = None):
        from fastapi import status

        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details or {},
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the RAG service."""

    @app.exception_handler(RAGServiceUnavailableError)
    async def rag_service_unavailable_handler(request: Request, exc: RAGServiceUnavailableError):
        """Handle RAGServiceUnavailableError exceptions."""
        logger.warning(f"RAG service unavailable: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(RAGQueryError)
    async def rag_query_error_handler(request: Request, exc: RAGQueryError):
        """Handle RAGQueryError exceptions."""
        logger.error(f"RAG query error: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(RAGStatsError)
    async def rag_stats_error_handler(request: Request, exc: RAGStatsError):
        """Handle RAGStatsError exceptions."""
        logger.error(f"RAG stats error: {exc}")
        return create_error_response(request, exc)
