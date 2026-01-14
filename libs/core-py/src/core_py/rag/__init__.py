"""
RAG Module

Retrieval-Augmented Generation service for querying knowledge base.
"""

from core_py.rag.dependency_injection import (
    get_rag_service_injected,
    get_rag_service_provider,
    set_rag_service_provider,
)
from core_py.rag.service import RagService, get_rag_service

__all__ = [
    "RagService",
    "get_rag_service",
    "get_rag_service_injected",
    "get_rag_service_provider",
    "set_rag_service_provider",
]
