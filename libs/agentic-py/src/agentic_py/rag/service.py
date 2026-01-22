"""
RAG Service

Provides retrieval-augmented generation capabilities for querying knowledge base
and retrieving relevant context for lesson generation.
"""

import asyncio
import time
from pathlib import Path
from typing import Any

from loguru import logger

from agentic_py.config.llm import EMBEDDING_MODEL
from agentic_py.config.rag import (
    FAISS_INDEX_PATH,
    PGVECTOR_COLLECTION,
    PGVECTOR_CONNECTION_STRING,
    RAG_ENABLED,
    RAG_INGESTION_BATCH_SIZE,
    RAG_TOP_K,
    VECTOR_STORE_TYPE,
)
from agentic_py.rag.ingestion import ingest_directory, ingest_document

# Re-export for backward compatibility
__all__ = ["RagService", "get_rag_service", "RAG_ENABLED", "RAG_TOP_K"]


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
        self._init_lock = asyncio.Lock()  # Prevent concurrent initialization

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
        start_time = time.time()
        top_k = top_k or RAG_TOP_K

        logger.debug(
            "RAG query started",
            extra={
                "query_length": len(query),
                "query_preview": query[:100] + "..." if len(query) > 100 else query,
                "error_patterns_count": len(error_patterns) if error_patterns else 0,
                "top_k": top_k,
                "enabled": self.enabled,
            },
        )

        if not self.enabled:
            logger.debug("RAG service is disabled, returning empty context")
            return "RAG service is not enabled. Set RAG_ENABLED=true to enable."

        try:
            # Initialize vector store if not already initialized
            init_start = time.time()
            if not self._vector_store:
                await self._initialize_vector_store()
            init_duration = time.time() - init_start
            if init_duration > 0.1:
                logger.debug(
                    "Vector store initialization completed",
                    extra={"duration_ms": init_duration * 1000},
                )

            if not self._vector_store:
                logger.warning(
                    "Vector store not initialized, returning empty context",
                    extra={"vector_store_type": VECTOR_STORE_TYPE},
                )
                return "Vector store not available. Please check configuration."

            # Enhance query with error patterns
            enhanced_query = self._enhance_query(query, error_patterns)
            if enhanced_query != query:
                logger.debug(
                    "Query enhanced with error patterns",
                    extra={
                        "original_length": len(query),
                        "enhanced_length": len(enhanced_query),
                    },
                )

            # Query vector store
            # Note: similarity_search is synchronous in LangChain, but we're in async context
            # Use asyncio.to_thread for async execution
            search_start = time.time()
            logger.debug(
                "Executing similarity search",
                extra={
                    "enhanced_query_length": len(enhanced_query),
                    "top_k": top_k,
                    "vector_store_type": VECTOR_STORE_TYPE,
                },
            )

            results = await asyncio.to_thread(
                self._vector_store.similarity_search,
                enhanced_query,
                k=top_k,
            )

            search_duration = time.time() - search_start
            logger.debug(
                "Similarity search completed",
                extra={
                    "results_count": len(results),
                    "top_k": top_k,
                    "duration_ms": search_duration * 1000,
                },
            )

            # Format results into context string
            format_start = time.time()
            context = self._format_results(results)
            format_duration = time.time() - format_start

            total_duration = time.time() - start_time
            logger.info(
                "RAG query completed successfully",
                extra={
                    "query_length": len(query),
                    "results_count": len(results),
                    "top_k": top_k,
                    "context_length": len(context),
                    "init_duration_ms": init_duration * 1000,
                    "search_duration_ms": search_duration * 1000,
                    "format_duration_ms": format_duration * 1000,
                    "total_duration_ms": total_duration * 1000,
                    "vector_store_type": VECTOR_STORE_TYPE,
                },
            )
            return context

        except Exception as e:
            total_duration = time.time() - start_time
            logger.error(
                "RAG query failed",
                extra={
                    "query_length": len(query),
                    "query_preview": query[:100] + "..." if len(query) > 100 else query,
                    "top_k": top_k,
                    "duration_ms": total_duration * 1000,
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
        Uses a lock to prevent concurrent initialization.
        """
        # Check again after acquiring lock (double-check pattern)
        if self._vector_store is not None:
            logger.debug("Vector store already initialized")
            return

        async with self._init_lock:
            # Double-check after acquiring lock
            if self._vector_store is not None:
                logger.debug("Vector store already initialized (checked after lock)")
                return

        try:
            logger.debug(
                "Initializing embedding model",
                extra={"model": EMBEDDING_MODEL},
            )
            from langchain_openai import OpenAIEmbeddings

            # Initialize embedding model
            self._embedding_model = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
            )
            logger.debug(
                "Embedding model initialized",
                extra={"model": EMBEDDING_MODEL},
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
                "For pgvector: pip install langchain-community pgvector. "
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

    async def ingest_document(
        self, path: str | Path, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Ingest a single document into the vector store.

        Loads, chunks, and adds a document to the vector store.

        Args:
            path: Path to the document file
            metadata: Optional metadata to override or add to document metadata

        Raises:
            FileNotFoundError: If document doesn't exist
            RuntimeError: If vector store is not initialized

        Example:
            >>> service = RagService(enabled=True)
            >>> await service.ingest_document("docs/guide.md")
        """
        if not self.enabled:
            logger.warning("RAG service is disabled, skipping ingestion")
            return

        # Initialize vector store if needed
        if not self._vector_store:
            await self._initialize_vector_store()

        if not self._vector_store:
            raise RuntimeError(
                "Vector store not initialized. Cannot ingest documents. "
                "Check vector store configuration."
            )

        # Ingest and chunk the document
        documents = await ingest_document(path, metadata_override=metadata)

        if not documents:
            logger.warning(f"No chunks created for {path}")
            return

        # Add documents to vector store
        # Note: LangChain vector stores use synchronous add_documents, so we run in executor
        await asyncio.to_thread(self._vector_store.add_documents, documents)

        # For FAISS, save the index after adding documents
        if VECTOR_STORE_TYPE == "faiss":
            await asyncio.to_thread(self._vector_store.save_local, FAISS_INDEX_PATH)

        logger.info(
            "Document ingested successfully",
            extra={
                "path": str(path),
                "chunks": len(documents),
                "vector_store_type": VECTOR_STORE_TYPE,
            },
        )

    async def ingest_directory(
        self,
        directory: str | Path,
        file_patterns: list[str] | None = None,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """
        Ingest all documents in a directory into the vector store.

        Args:
            directory: Directory to ingest
            file_patterns: File patterns to match (e.g., ["*.md", "*.py"])
            recursive: Whether to search recursively

        Returns:
            Dictionary with ingestion statistics:
            {
                "files_processed": int,
                "total_chunks": int,
                "errors": list[str]
            }

        Example:
            >>> result = await service.ingest_directory("docs", file_patterns=["*.md"])
            >>> result["files_processed"]
            10
        """
        if not self.enabled:
            logger.warning("RAG service is disabled, skipping ingestion")
            return {
                "files_processed": 0,
                "total_chunks": 0,
                "errors": ["RAG service is disabled"],
            }

        # Initialize vector store if needed
        if not self._vector_store:
            await self._initialize_vector_store()

        if not self._vector_store:
            raise RuntimeError(
                "Vector store not initialized. Cannot ingest documents. "
                "Check vector store configuration."
            )

        # Ingest directory
        result = await ingest_directory(directory, file_patterns=file_patterns, recursive=recursive)

        documents = result["documents"]
        if not documents:
            logger.warning(f"No documents found in {directory}")
            return {
                "files_processed": 0,
                "total_chunks": 0,
                "errors": result["errors"],
            }

        # Add documents to vector store in batches
        # Note: LangChain vector stores use synchronous add_documents, so we run in executor
        batch_size = RAG_INGESTION_BATCH_SIZE

        def _add_documents_batch(docs: list[Any]) -> None:
            """Helper function to add documents batch."""
            self._vector_store.add_documents(docs)

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            await asyncio.to_thread(_add_documents_batch, batch)
            logger.debug(
                f"Added batch {i // batch_size + 1} to vector store",
                extra={"batch_size": len(batch), "total": len(documents)},
            )

        # For FAISS, save the index after adding all documents
        if VECTOR_STORE_TYPE == "faiss":
            await asyncio.to_thread(self._vector_store.save_local, FAISS_INDEX_PATH)

        logger.info(
            "Directory ingestion completed",
            extra={
                "directory": str(directory),
                "files_processed": result["files_processed"],
                "total_chunks": result["total_chunks"],
                "errors": len(result["errors"]),
            },
        )

        return {
            "files_processed": result["files_processed"],
            "total_chunks": result["total_chunks"],
            "errors": result["errors"],
        }

    async def delete_document(self, source: str) -> None:  # noqa: ARG002
        """
        Delete a document from the vector store by source path.

        Note: This method only works with pgvector. FAISS doesn't support
        document deletion without rebuilding the index.

        Args:
            source: Source path of the document to delete

        Raises:
            NotImplementedError: If using FAISS (deletion not supported)
            RuntimeError: If vector store is not initialized

        Example:
            >>> await service.delete_document("docs/guide.md")
        """
        if not self.enabled:
            logger.warning("RAG service is disabled, skipping deletion")
            return

        if not self._vector_store:
            raise RuntimeError("Vector store not initialized")

        if VECTOR_STORE_TYPE == "faiss":
            raise NotImplementedError(
                "Document deletion is not supported for FAISS. "
                "Rebuild the index or use pgvector for production deployments."
            )

        # For pgvector, we need to delete by metadata filter
        # LangChain PGVector doesn't have a direct delete method, so we'd need
        # to use the underlying connection. This is not yet implemented.
        raise NotImplementedError(
            "Document deletion by source is not yet fully implemented for pgvector. "
            "Consider rebuilding the index or implementing custom deletion logic using "
            "metadata filters. This feature will be available in a future release."
        )

    async def list_documents(self) -> list[dict[str, Any]]:
        """
        List documents in the vector store (for debugging).

        Returns metadata about documents in the vector store.

        Args:
            None

        Returns:
            List of document metadata dictionaries

        Note:
            This is a debugging utility. Implementation depends on vector store type.
            For FAISS, this may not be fully supported.

        Example:
            >>> docs = await service.list_documents()
            >>> len(docs)
            10
        """
        if not self.enabled:
            logger.warning("RAG service is disabled")
            return []

        if not self._vector_store:
            logger.warning("Vector store not initialized")
            return []

        # For pgvector, we could query the database directly
        # For FAISS, this is more limited
        # This feature is not yet implemented
        raise NotImplementedError(
            "list_documents() is not yet fully implemented. "
            "Consider querying the vector store directly for debugging. "
            "This feature will be available in a future release."
        )


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
