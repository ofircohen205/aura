"""
RAG Service

Provides retrieval-augmented generation capabilities for querying knowledge base
and retrieving relevant context for lesson generation.
"""

import logging
from typing import Any

from core_py.ml.config import (
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    PGVECTOR_COLLECTION,
    PGVECTOR_CONNECTION_STRING,
    RAG_ENABLED,
    RAG_TOP_K,
    VECTOR_STORE_TYPE,
)

# Re-export for backward compatibility
__all__ = ["RagService", "get_rag_service", "RAG_ENABLED", "RAG_TOP_K"]

logger = logging.getLogger(__name__)


class RagService:
    """
    RAG Service for querying vector store and retrieving relevant context.

    This service provides an interface for querying a vector store (pgvector/FAISS)
    to retrieve relevant documentation and code examples based on error patterns
    and user struggles.

    Supports both pgvector (PostgreSQL extension) for production and FAISS for
    local development/testing.
    """

    def __init__(self, enabled: bool = False):
        """
        Initialize RAG Service.

        Args:
            enabled: Whether RAG is enabled (defaults to RAG_ENABLED env var)
        """
        self.enabled = enabled or RAG_ENABLED
        self._vector_store = None
        self._embedding_model = None

    async def query_knowledge(
        self, query: str, error_patterns: list[str] | None = None, top_k: int | None = None
    ) -> str:
        """
        Query the vector store for relevant knowledge based on the query and error patterns.

        Args:
            query: Main query string (e.g., error message or struggle description)
            error_patterns: List of error patterns to enhance the query
            top_k: Number of documents to retrieve (defaults to RAG_TOP_K)

        Returns:
            Formatted context string with relevant documentation/examples
        """
        if not self.enabled:
            logger.debug("RAG service is disabled, returning empty context")
            return "RAG service is not enabled. Set RAG_ENABLED=true to enable."

        top_k = top_k or RAG_TOP_K

        try:
            # Initialize vector store if not already initialized
            if not self._vector_store:
                await self._initialize_vector_store()

            if not self._vector_store:
                logger.warning(
                    "Vector store not initialized, returning empty context",
                    extra={"vector_store_type": VECTOR_STORE_TYPE},
                )
                return "Vector store not available. Please check configuration."

            # Enhance query with error patterns
            enhanced_query = self._enhance_query(query, error_patterns)

            # Query vector store
            # Note: similarity_search is synchronous in LangChain, but we're in async context
            # For production, consider using async vector stores or running in executor
            import asyncio

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self._vector_store.similarity_search(
                    enhanced_query,
                    k=top_k,
                ),
            )

            # Format results into context string
            context = self._format_results(results)
            logger.debug(
                "RAG query completed",
                extra={
                    "query": query[:100],
                    "results_count": len(results),
                    "top_k": top_k,
                },
            )
            return context

        except Exception as e:
            logger.error(
                "RAG query failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "vector_store_type": VECTOR_STORE_TYPE,
                },
                exc_info=True,
            )
            # Return fallback message instead of raising to avoid breaking workflows
            return (
                f"RAG query failed: {type(e).__name__}. "
                f"Query: {query[:100]}{'...' if len(query) > 100 else ''}. "
                f"Please check vector store configuration."
            )

    async def _initialize_vector_store(self) -> None:
        """
        Initialize the vector store connection.

        Supports both pgvector (PostgreSQL extension) and FAISS for local development.
        """
        if self._vector_store is not None:
            logger.debug("Vector store already initialized")
            return

        try:
            from langchain_openai import OpenAIEmbeddings

            # Initialize embedding model
            self._embedding_model = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
            )

            if VECTOR_STORE_TYPE == "pgvector":
                await self._initialize_pgvector()
            elif VECTOR_STORE_TYPE == "faiss":
                await self._initialize_faiss()
            else:
                raise ValueError(
                    f"Unsupported vector store type: {VECTOR_STORE_TYPE}. "
                    f"Supported types: pgvector, faiss"
                )

            logger.info(
                "Vector store initialized successfully",
                extra={"vector_store_type": VECTOR_STORE_TYPE},
            )

        except ImportError as e:
            logger.error(
                f"Required package not installed for {VECTOR_STORE_TYPE}: {e}",
                exc_info=True,
            )
            raise ImportError(
                "Vector store dependencies not installed. "
                "For pgvector: pip install langchain-pgvector pgvector. "
                "For FAISS: pip install langchain-community faiss-cpu"
            ) from e
        except Exception as e:
            logger.error(
                f"Failed to initialize vector store: {e}",
                extra={"vector_store_type": VECTOR_STORE_TYPE},
                exc_info=True,
            )
            raise

    async def _initialize_pgvector(self) -> None:
        """Initialize pgvector (PostgreSQL extension) vector store."""
        try:
            from langchain_community.vectorstores import PGVector

            self._vector_store = PGVector(
                connection=PGVECTOR_CONNECTION_STRING,
                embedding_function=self._embedding_model,
                collection_name=PGVECTOR_COLLECTION,
                use_jsonb=True,  # Use JSONB for metadata for better performance
            )

            logger.debug(
                "pgvector initialized",
                extra={
                    "collection": PGVECTOR_COLLECTION,
                    "connection_string": PGVECTOR_CONNECTION_STRING.split("@")[
                        -1
                    ],  # Hide credentials in logs
                },
            )

        except Exception as e:
            logger.error(f"Failed to initialize pgvector: {e}", exc_info=True)
            raise RuntimeError(
                "pgvector initialization failed. "
                "Ensure PostgreSQL has the pgvector extension installed: "
                "CREATE EXTENSION vector;"
            ) from e

    async def _initialize_faiss(self) -> None:
        """Initialize FAISS vector store for local development."""
        try:
            from pathlib import Path

            from langchain_community.vectorstores import FAISS

            index_path = Path(FAISS_INDEX_PATH)

            # Try to load existing index if it exists
            if index_path.exists() and (index_path / "index.faiss").exists():
                logger.debug(f"Loading existing FAISS index from {FAISS_INDEX_PATH}")
                self._vector_store = FAISS.load_local(
                    str(index_path),
                    self._embedding_model,
                    allow_dangerous_deserialization=True,  # Required for FAISS
                )
            else:
                logger.warning(
                    f"FAISS index not found at {FAISS_INDEX_PATH}, "
                    f"creating empty vector store. "
                    f"Use FAISS.from_documents() to populate it."
                )
                # Create empty FAISS store - will need to be populated separately
                # WARNING: FAISS doesn't have a direct delete method, so we create a minimal
                # placeholder document to initialize the store. This placeholder will remain
                # in the index and may appear in search results until the index is rebuilt.
                # For production use, prefer pgvector which supports proper document management.
                from langchain_core.documents import Document

                self._vector_store = FAISS.from_documents(
                    [Document(page_content="placeholder", metadata={})],
                    self._embedding_model,
                )
                logger.warning(
                    "FAISS initialized with placeholder document. "
                    "Placeholder may appear in search results. "
                    "Consider using pgvector for production deployments."
                )

            logger.debug(f"FAISS initialized from {FAISS_INDEX_PATH}")

        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}", exc_info=True)
            raise RuntimeError(f"FAISS initialization failed: {e}") from e

    def _enhance_query(self, query: str, error_patterns: list[str] | None) -> str:
        """
        Enhance the query with error patterns for better retrieval.

        Combines the base query with error patterns to create a more comprehensive
        search query. This helps the vector store find more relevant documentation
        by including context from error messages.

        Args:
            query: Base query string (e.g., error message or struggle description)
            error_patterns: Optional list of error patterns to append to the query.
                If None or empty, returns the original query unchanged.

        Returns:
            Enhanced query string combining the base query and error patterns.
            If error_patterns is None or empty, returns the original query.

        Example:
            >>> service._enhance_query("TypeError", ["NoneType", "not callable"])
            "TypeError NoneType not callable"
        """
        if not error_patterns:
            return query

        # Combine query with error patterns
        error_context = " ".join(error_patterns)
        return f"{query} {error_context}"

    def _format_results(self, results: list[Any]) -> str:
        """
        Format vector store results into a context string.

        Takes a list of document objects from the vector store and formats them
        into a readable context string with source attribution.

        Args:
            results: List of retrieved documents from vector store.
                Each document should have `page_content` and `metadata` attributes
                (LangChain document format).

        Returns:
            Formatted context string with document content and source information.
            Returns "No relevant documentation found." if results list is empty.

        Example:
            >>> results = [Document(page_content="...", metadata={"source": "file.md"})]
            >>> service._format_results(results)
            "### Document 1 (from file.md)\\n...\\n"
        """
        if not results:
            return "No relevant documentation found."

        formatted = []
        for i, doc in enumerate(results, 1):
            content = doc.page_content if hasattr(doc, "page_content") else str(doc)
            metadata = doc.metadata if hasattr(doc, "metadata") else {}
            source = metadata.get("source", "unknown")

            formatted.append(f"### Document {i} (from {source})\n{content}\n")

        return "\n".join(formatted)


# Global RAG service instance (for backward compatibility)
# Note: For production use, consider dependency injection instead of global singleton
_rag_service: RagService | None = None


def get_rag_service(enabled: bool | None = None) -> RagService:
    """
    Get the global RAG service instance.

    This function provides a singleton pattern for backward compatibility.
    For better testability and dependency injection, consider creating
    RagService instances directly.

    Args:
        enabled: Optional override for RAG enabled state.
            If None, uses RAG_ENABLED from config.

    Returns:
        RagService instance

    Note:
        The global singleton pattern is used for convenience but may cause
        issues in async contexts. For production, consider using dependency
        injection to create service instances per request/context.
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService(enabled=enabled)
    elif enabled is not None and _rag_service.enabled != enabled:
        # Recreate if enabled state changed
        _rag_service = RagService(enabled=enabled)
    return _rag_service
