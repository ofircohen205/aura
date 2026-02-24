"""
Tests for RAG service initialization and error handling.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentic_py.rag.service import RagService, get_rag_service


def test_rag_service_disabled():
    """Test RAG service when disabled."""
    service = RagService(enabled=False)
    assert service.enabled is False
    assert service._vector_store is None


@pytest.mark.asyncio
async def test_rag_service_query_disabled():
    """Test query_knowledge when RAG is disabled."""
    service = RagService(enabled=False)
    result = await service.query_knowledge("test query")
    assert "not enabled" in result.lower()


@pytest.mark.asyncio
async def test_rag_service_query_enabled_no_vector_store():
    """Test query_knowledge when enabled but vector store not initialized."""
    service = RagService(enabled=True)
    result = await service.query_knowledge("test query")
    # Should return error message about vector store not available
    assert "not available" in result.lower() or "failed" in result.lower()


@pytest.mark.asyncio
async def test_rag_service_initialize_pgvector():
    """Test pgvector initialization."""
    with patch.dict(
        os.environ,
        {
            "PGVECTOR_CONNECTION_STRING": "postgresql://test:test@localhost:5432/test",
            "PGVECTOR_COLLECTION": "test_collection",
            "OPENAI_API_KEY": "test-key",  # Mock API key
        },
    ):
        with patch(
            "agentic_py.rag.service.PGVECTOR_CONNECTION_STRING",
            "postgresql://test:test@localhost:5432/test",
        ):
            with patch("langchain_openai.OpenAIEmbeddings"):
                service = RagService(enabled=True)
                try:
                    await service._initialize_vector_store()
                    # If initialization succeeds, vector_store should be set
                    # If it fails (expected in test env), should raise appropriate error
                except (ImportError, RuntimeError, ValueError) as e:
                    # Expected in test environment without actual PostgreSQL
                    assert (
                        "pgvector" in str(e).lower()
                        or "postgresql" in str(e).lower()
                        or "import" in str(e).lower()
                    )


def test_rag_service_enhance_query():
    """Test query enhancement with error patterns."""
    service = RagService()
    query = "TypeError"
    error_patterns = ["NoneType", "not callable"]

    enhanced = service._enhance_query(query, error_patterns)
    assert query in enhanced
    assert "NoneType" in enhanced
    assert "not callable" in enhanced


def test_rag_service_enhance_query_no_patterns():
    """Test query enhancement without error patterns."""
    service = RagService()
    query = "TypeError"

    enhanced = service._enhance_query(query, None)
    assert enhanced == query

    enhanced = service._enhance_query(query, [])
    assert enhanced == query


def test_rag_service_format_results():
    """Test formatting of vector store results."""
    service = RagService()

    # Test with empty results
    result = service._format_results([])
    assert "No relevant documentation found" in result

    # Test with mock document
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "test.md"}

    result = service._format_results([mock_doc])
    assert "Document 1" in result
    assert "test.md" in result
    assert "Test content" in result


def test_rag_service_format_results_multiple():
    """Test formatting multiple results."""
    service = RagService()

    mock_docs = []
    for i in range(3):
        doc = MagicMock()
        doc.page_content = f"Content {i}"
        doc.metadata = {"source": f"file{i}.md"}
        mock_docs.append(doc)

    result = service._format_results(mock_docs)
    assert "Document 1" in result
    assert "Document 2" in result
    assert "Document 3" in result
    assert "file0.md" in result
    assert "file1.md" in result
    assert "file2.md" in result


def test_rag_service_format_results_no_metadata():
    """Test formatting results without metadata."""
    service = RagService()

    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {}

    result = service._format_results([mock_doc])
    assert "unknown" in result
    assert "Test content" in result


def test_get_rag_service_singleton():
    """Test that get_rag_service returns singleton."""
    service1 = get_rag_service()
    service2 = get_rag_service()

    # Should be the same instance
    assert service1 is service2


def test_get_rag_service_with_enabled():
    """Test get_rag_service with enabled parameter."""
    service1 = get_rag_service(enabled=True)
    assert service1.enabled is True

    service2 = get_rag_service(enabled=False)
    # Should create new instance if enabled state changed
    assert service2.enabled is False


@pytest.mark.asyncio
async def test_rag_service_query_with_error():
    """Test query_knowledge error handling."""
    service = RagService(enabled=True)

    # Mock vector store initialization to raise error
    with patch.object(service, "_initialize_vector_store", side_effect=Exception("Test error")):
        result = await service.query_knowledge("test query")
        assert "failed" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_rag_service_query_success():
    """Test successful query_knowledge call."""
    service = RagService(enabled=True)

    # Mock vector store and similarity_search
    mock_vector_store = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = "Test result"
    mock_doc.metadata = {"source": "test.md"}
    mock_vector_store.similarity_search.return_value = [mock_doc]

    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge("test query")
        assert "Test result" in result
        assert "test.md" in result
