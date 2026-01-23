"""
Tests for RAG API endpoints.

Tests the RAG API v1 endpoints including query and stats endpoints.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Add backend directory to path for conf import
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402

# Import the API v1 RAG app
from api.dependencies import get_current_active_user  # noqa: E402
from api.v1.rag.endpoints import create_rag_app  # noqa: E402
from db.models.user import User  # noqa: E402

# Create a test app using the API v1 RAG app
test_app = create_rag_app()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    from datetime import UTC, datetime
    from uuid import uuid4

    return User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        is_active=True,
        is_verified=True,
        roles=["user"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture(autouse=True)
def override_auth_dependency(mock_user):
    """Override authentication dependency for all tests."""

    async def mock_get_current_active_user():
        return mock_user

    test_app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    yield
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service for testing."""
    service = MagicMock()
    service.query_knowledge = AsyncMock(return_value="Test context from RAG service")
    return service


@pytest.mark.asyncio
async def test_query_rag_success(mock_rag_service):
    """Test successful RAG query."""
    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "How do I use a for loop in Python?",
                "error_patterns": ["NameError"],
                "top_k": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        assert "query" in data
        assert "top_k" in data
        assert data["query"] == "How do I use a for loop in Python?"
        assert data["top_k"] == 5
        assert "Test context" in data["context"]

        # Verify service was called correctly
        mock_rag_service.query_knowledge.assert_called_once()
        call_args = mock_rag_service.query_knowledge.call_args
        assert call_args.kwargs["query"] == "How do I use a for loop in Python?"
        assert call_args.kwargs["error_patterns"] == ["NameError"]
        assert call_args.kwargs["top_k"] == 5


@pytest.mark.asyncio
async def test_query_rag_without_error_patterns(mock_rag_service):
    """Test RAG query without error patterns."""
    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "Python list comprehension",
                "top_k": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Python list comprehension"
        assert data["top_k"] == 3

        # Verify service was called with None error_patterns
        call_args = mock_rag_service.query_knowledge.call_args
        assert call_args.kwargs["error_patterns"] is None


@pytest.mark.asyncio
async def test_query_rag_default_top_k(mock_rag_service):
    """Test RAG query with default top_k."""
    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "TypeScript async await",
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Default top_k is 5
        assert data["top_k"] == 5


@pytest.mark.asyncio
async def test_query_rag_disabled():
    """Test RAG query when service is disabled."""
    with patch("api.v1.rag.endpoints.RAG_ENABLED", False):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "Test query",
            },
        )

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "not enabled" in data["detail"].lower()


@pytest.mark.asyncio
async def test_query_rag_invalid_top_k():
    """Test RAG query with invalid top_k values."""
    with patch("api.v1.rag.endpoints.RAG_ENABLED", True):
        client = TestClient(test_app)

        # Test top_k too high
        response = client.post(
            "/rag/query",
            json={
                "query": "Test query",
                "top_k": 100,  # Max is 50
            },
        )
        assert response.status_code == 422

        # Test top_k too low
        response = client.post(
            "/rag/query",
            json={
                "query": "Test query",
                "top_k": 0,  # Min is 1
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_query_rag_missing_query():
    """Test RAG query with missing query field."""
    with patch("api.v1.rag.endpoints.RAG_ENABLED", True):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={},
        )

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_query_rag_service_error(mock_rag_service):
    """Test RAG query when service raises an error."""
    mock_rag_service.query_knowledge = AsyncMock(side_effect=Exception("Service error"))

    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "Test query",
            },
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "failed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_rag_stats_success():
    """Test successful RAG stats retrieval."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    # Mock collection query result
    mock_collection_row = MagicMock()
    mock_collection_row.__getitem__.side_effect = lambda idx: (
        "test-uuid" if idx == 0 else "test_collection"
    )
    mock_result.fetchone.return_value = mock_collection_row

    # Mock count queries
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 100  # total_chunks
    mock_docs_result = MagicMock()
    mock_docs_result.scalar.return_value = 10  # total_documents

    # Mock language/difficulty breakdown queries
    mock_lang_result = MagicMock()
    mock_lang_result.fetchall.return_value = [
        ("python", 50),
        ("typescript", 30),
        ("java", 20),
    ]
    mock_diff_result = MagicMock()
    mock_diff_result.fetchall.return_value = [
        ("beginner", 40),
        ("intermediate", 35),
        ("advanced", 25),
    ]

    mock_db.execute.side_effect = [
        mock_result,  # collection query
        mock_count_result,  # chunks count
        mock_docs_result,  # documents count
        mock_lang_result,  # language breakdown
        mock_diff_result,  # difficulty breakdown
    ]

    with (
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
        patch("api.v1.rag.endpoints.SessionDep") as mock_session_dep,
        patch("api.v1.rag.endpoints.PGVECTOR_COLLECTION", "test_collection"),
    ):
        mock_session_dep.return_value = mock_db
        client = TestClient(test_app)
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 10
        assert data["total_chunks"] == 100
        assert data["collection_name"] == "test_collection"
        assert data["documents_by_language"]["python"] == 50
        assert data["documents_by_language"]["typescript"] == 30
        assert data["documents_by_language"]["java"] == 20
        assert data["documents_by_difficulty"]["beginner"] == 40
        assert data["documents_by_difficulty"]["intermediate"] == 35
        assert data["documents_by_difficulty"]["advanced"] == 25


@pytest.mark.asyncio
async def test_get_rag_stats_no_collection():
    """Test RAG stats when collection doesn't exist."""
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None  # No collection found

    mock_db.execute.return_value = mock_result

    with (
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
        patch("api.v1.rag.endpoints.SessionDep") as mock_session_dep,
        patch("api.v1.rag.endpoints.PGVECTOR_COLLECTION", "nonexistent"),
    ):
        mock_session_dep.return_value = mock_db
        client = TestClient(test_app)
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 0
        assert data["total_chunks"] == 0
        assert data["collection_name"] == "nonexistent"
        assert data["documents_by_language"] == {}
        assert data["documents_by_difficulty"] == {}


@pytest.mark.asyncio
async def test_get_rag_stats_disabled():
    """Test RAG stats when service is disabled."""
    with patch("api.v1.rag.endpoints.RAG_ENABLED", False):
        client = TestClient(test_app)
        response = client.get("/stats")

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "not enabled" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_rag_stats_database_error():
    """Test RAG stats when database query fails."""
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Database error")

    with (
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
        patch("api.v1.rag.endpoints.SessionDep") as mock_session_dep,
    ):
        mock_session_dep.return_value = mock_db
        client = TestClient(test_app)
        response = client.get("/stats")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "failed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_query_rag_empty_error_patterns(mock_rag_service):
    """Test RAG query with empty error patterns list."""
    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "Test query",
                "error_patterns": [],
            },
        )

        assert response.status_code == 200
        # Empty list should be treated as None
        call_args = mock_rag_service.query_knowledge.call_args
        assert call_args.kwargs["error_patterns"] == []


@pytest.mark.asyncio
async def test_query_rag_multiple_error_patterns(mock_rag_service):
    """Test RAG query with multiple error patterns."""
    with (
        patch("api.v1.rag.endpoints.RagService", return_value=mock_rag_service),
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
    ):
        client = TestClient(test_app)
        response = client.post(
            "/query",
            json={
                "query": "TypeError in Python",
                "error_patterns": [
                    "TypeError: unsupported operand type",
                    "NoneType object is not callable",
                ],
                "top_k": 10,
            },
        )

        assert response.status_code == 200
        call_args = mock_rag_service.query_knowledge.call_args
        assert len(call_args.kwargs["error_patterns"]) == 2
        assert "TypeError: unsupported operand type" in call_args.kwargs["error_patterns"]


@pytest.mark.asyncio
async def test_get_rag_stats_empty_breakdowns():
    """Test RAG stats with no language/difficulty metadata."""
    mock_db = MagicMock()
    mock_collection_result = MagicMock()
    mock_collection_row = MagicMock()
    mock_collection_row.__getitem__.side_effect = lambda idx: (
        "test-uuid" if idx == 0 else "test_collection"
    )
    mock_collection_result.fetchone.return_value = mock_collection_row

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 50
    mock_docs_result = MagicMock()
    mock_docs_result.scalar.return_value = 5

    # Empty breakdowns
    mock_lang_result = MagicMock()
    mock_lang_result.fetchall.return_value = []
    mock_diff_result = MagicMock()
    mock_diff_result.fetchall.return_value = []

    mock_db.execute.side_effect = [
        mock_collection_result,
        mock_count_result,
        mock_docs_result,
        mock_lang_result,
        mock_diff_result,
    ]

    with (
        patch("api.v1.rag.endpoints.RAG_ENABLED", True),
        patch("api.v1.rag.endpoints.SessionDep") as mock_session_dep,
        patch("api.v1.rag.endpoints.PGVECTOR_COLLECTION", "test_collection"),
    ):
        mock_session_dep.return_value = mock_db
        client = TestClient(test_app)
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 5
        assert data["total_chunks"] == 50
        assert data["documents_by_language"] == {}
        assert data["documents_by_difficulty"] == {}
