"""RAG API schemas."""

from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request schema for RAG query."""

    query: str = Field(..., max_length=5000, description="Search query")
    error_patterns: list[str] | None = Field(
        None, description="Optional error patterns to enhance query"
    )
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")


class RAGQueryResponse(BaseModel):
    """Response schema for RAG query."""

    context: str = Field(..., description="Retrieved context from vector store")
    query: str = Field(..., description="Original query")
    top_k: int = Field(..., description="Number of results requested")


class RAGDocumentMetadata(BaseModel):
    """Metadata for a document in the vector store."""

    source: str | None = None
    language: str | None = None
    difficulty: str | None = None
    title: str | None = None
    keywords: list[str] | None = None
    file_type: str | None = None


class RAGDocumentInfo(BaseModel):
    """Information about a document in the vector store."""

    id: str
    source: str | None = None
    language: str | None = None
    difficulty: str | None = None
    title: str | None = None
    content_preview: str | None = None
    metadata: dict | None = None


class RAGStatsResponse(BaseModel):
    """Statistics about the RAG vector store."""

    total_documents: int
    total_chunks: int
    documents_by_language: dict[str, int]
    documents_by_difficulty: dict[str, int]
    collection_name: str | None = None
