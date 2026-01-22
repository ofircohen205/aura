"""
Dependency Injection Support for RAG Service

Provides dependency injection pattern for RAG service to improve testability
and support per-request service instances.
"""

import logging
from typing import Protocol

from agentic_py.rag.service import RagService

logger = logging.getLogger(__name__)


class RagServiceProvider(Protocol):
    """Protocol for RAG service providers (dependency injection)."""

    def get_rag_service(self) -> RagService:
        """Get RAG service instance."""
        ...


class DefaultRagServiceProvider:
    """Default RAG service provider using singleton pattern."""

    def __init__(self):
        self._service: RagService | None = None

    def get_rag_service(self) -> RagService:
        """Get or create RAG service instance."""
        if self._service is None:
            self._service = RagService()
        return self._service


class PerRequestRagServiceProvider:
    """RAG service provider that creates new instance per request."""

    def get_rag_service(self, enabled: bool | None = None) -> RagService:
        """Create new RAG service instance for each request."""
        return RagService(enabled=enabled)


# Global provider instance (can be swapped for testing)
_rag_service_provider: RagServiceProvider = DefaultRagServiceProvider()


def set_rag_service_provider(provider: RagServiceProvider) -> None:
    """
    Set the RAG service provider for dependency injection.

    Useful for testing or custom service instantiation.

    Args:
        provider: Provider instance that implements RagServiceProvider protocol

    Example:
        >>> from agentic_py.rag.dependency_injection import set_rag_service_provider, PerRequestRagServiceProvider
        >>> set_rag_service_provider(PerRequestRagServiceProvider())
    """
    global _rag_service_provider
    _rag_service_provider = provider
    logger.info("RAG service provider updated", extra={"provider_type": type(provider).__name__})


def get_rag_service_provider() -> RagServiceProvider:
    """
    Get the current RAG service provider.

    Returns:
        Current RagServiceProvider instance
    """
    return _rag_service_provider


def get_rag_service_injected(enabled: bool | None = None) -> RagService:
    """
    Get RAG service using dependency injection pattern.

    This function uses the configured provider to get a service instance.
    For production, use DefaultRagServiceProvider (singleton).
    For testing, use PerRequestRagServiceProvider or a mock.

    Args:
        enabled: Optional override for RAG enabled state

    Returns:
        RagService instance from the configured provider
    """
    provider = get_rag_service_provider()

    # Handle providers that support enabled parameter
    if isinstance(provider, PerRequestRagServiceProvider):
        return provider.get_rag_service(enabled=enabled)

    return provider.get_rag_service()
