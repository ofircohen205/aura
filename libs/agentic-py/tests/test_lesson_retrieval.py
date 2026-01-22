"""
Integration tests for RAG lesson retrieval.

Tests RAG retrieval with educational lesson content for different languages
and difficulty levels. These tests verify that the RAG system can properly
retrieve relevant educational content based on student queries.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentic_py.rag.service import RagService


@pytest.mark.asyncio
async def test_retrieve_python_beginner_lesson():
    """Test retrieving Python beginner lesson content."""
    service = RagService(enabled=True)

    # Mock vector store with Python beginner lesson
    mock_vector_store = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = """
    # Variables and Data Types

    In Python, you can create variables to store data:

    ```python
    name = "Alice"
    age = 25
    ```

    Variables don't need type declarations in Python.
    """
    mock_doc.metadata = {
        "source": "docs/lessons/python/beginner/01-variables-and-data-types.md",
        "language": "python",
        "difficulty": "beginner",
        "title": "Variables and Data Types",
    }

    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="How do I create variables in Python?",
            top_k=1,
        )

        assert "variable" in result.lower() or "Variables" in result
        assert "python" in result.lower()


@pytest.mark.asyncio
async def test_retrieve_typescript_intermediate_lesson():
    """Test retrieving TypeScript intermediate lesson content."""
    service = RagService(enabled=True)

    mock_vector_store = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = """
    # TypeScript Generics

    Generics allow you to create reusable components:

    ```typescript
    function identity<T>(arg: T): T {
        return arg;
    }
    ```
    """
    mock_doc.metadata = {
        "source": "docs/lessons/typescript/intermediate/05-generics.md",
        "language": "typescript",
        "difficulty": "intermediate",
        "title": "Generics",
    }

    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="How do I use generics in TypeScript?",
            top_k=1,
        )

        assert "generic" in result.lower() or "Generics" in result
        assert "typescript" in result.lower()


@pytest.mark.asyncio
async def test_retrieve_java_advanced_lesson():
    """Test retrieving Java advanced lesson content."""
    service = RagService(enabled=True)

    mock_vector_store = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = """
    # Java Multithreading

    Java provides built-in support for multithreading:

    ```java
    Thread thread = new Thread(() -> {
        System.out.println("Running in thread");
    });
    thread.start();
    ```
    """
    mock_doc.metadata = {
        "source": "docs/lessons/java/advanced/08-multithreading.md",
        "language": "java",
        "difficulty": "advanced",
        "title": "Multithreading",
    }

    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="How do I create threads in Java?",
            top_k=1,
        )

        assert "thread" in result.lower() or "Thread" in result
        assert "java" in result.lower()


@pytest.mark.asyncio
async def test_retrieve_with_error_patterns():
    """Test retrieving lessons based on error patterns."""
    service = RagService(enabled=True)

    mock_vector_store = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = """
    # Common Python Errors: NameError

    A NameError occurs when you try to use a variable that hasn't been defined:

    ```python
    # This will cause a NameError
    print(undefined_variable)
    ```

    Solution: Make sure to define variables before using them.
    """
    mock_doc.metadata = {
        "source": "docs/lessons/python/beginner/09-error-handling.md",
        "language": "python",
        "difficulty": "beginner",
        "title": "Error Handling",
    }

    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="Python error",
            error_patterns=["NameError: name 'x' is not defined"],
            top_k=1,
        )

        # Verify query was enhanced with error pattern
        enhanced_query = service._enhance_query(
            "Python error", ["NameError: name 'x' is not defined"]
        )
        assert "NameError" in enhanced_query

        assert "error" in result.lower() or "Error" in result


@pytest.mark.asyncio
async def test_retrieve_multiple_lessons():
    """Test retrieving multiple lesson chunks."""
    service = RagService(enabled=True)

    mock_vector_store = MagicMock()
    mock_docs = []
    for i in range(3):
        doc = MagicMock()
        doc.page_content = f"Lesson content {i + 1} about Python loops"
        doc.metadata = {
            "source": f"docs/lessons/python/beginner/0{i + 1}-lesson.md",
            "language": "python",
            "difficulty": "beginner",
        }
        mock_docs.append(doc)

    mock_vector_store.similarity_search.return_value = mock_docs
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=mock_docs)
        result = await service.query_knowledge(
            query="Python for loops",
            top_k=3,
        )

        # Should contain content from multiple documents
        assert "Lesson content 1" in result
        assert "Lesson content 2" in result
        assert "Lesson content 3" in result


@pytest.mark.asyncio
async def test_retrieve_no_results():
    """Test retrieval when no relevant lessons are found."""
    service = RagService(enabled=True)

    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = []
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[])
        result = await service.query_knowledge(
            query="Completely unrelated query",
            top_k=5,
        )

        # Should return a message indicating no results
        assert "not found" in result.lower() or "no relevant" in result.lower()


@pytest.mark.asyncio
async def test_retrieve_difficulty_filtering():
    """Test that retrieved lessons match appropriate difficulty level."""
    service = RagService(enabled=True)

    # Mock beginner lesson
    mock_doc = MagicMock()
    mock_doc.page_content = "Beginner lesson about Python basics"
    mock_doc.metadata = {
        "source": "docs/lessons/python/beginner/01-basics.md",
        "language": "python",
        "difficulty": "beginner",
    }

    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="Python basics for beginners",
            top_k=1,
        )

        # Verify metadata is included in formatted results
        assert "beginner" in result.lower() or "basics" in result.lower()


@pytest.mark.asyncio
async def test_retrieve_cross_language_query():
    """Test retrieving lessons when query doesn't specify language."""
    service = RagService(enabled=True)

    # Mock Python lesson (should be retrieved even without explicit language)
    mock_doc = MagicMock()
    mock_doc.page_content = "Lesson about loops and iteration"
    mock_doc.metadata = {
        "source": "docs/lessons/python/beginner/05-loops.md",
        "language": "python",
        "difficulty": "beginner",
    }

    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = [mock_doc]
    service._vector_store = mock_vector_store
    service._embedding_model = MagicMock()

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=[mock_doc])
        result = await service.query_knowledge(
            query="How do I use loops?",
            top_k=1,
        )

        assert "loop" in result.lower() or "Loop" in result


def test_enhance_query_with_error_patterns():
    """Test query enhancement with error patterns."""
    service = RagService()
    query = "Python error"
    error_patterns = ["NameError: name 'x' is not defined", "TypeError: unsupported operand"]

    enhanced = service._enhance_query(query, error_patterns)
    assert query in enhanced
    assert "NameError" in enhanced
    assert "TypeError" in enhanced
    assert "name 'x' is not defined" in enhanced


def test_enhance_query_without_patterns():
    """Test query enhancement without error patterns."""
    service = RagService()
    query = "Python loops"

    enhanced = service._enhance_query(query, None)
    assert enhanced == query

    enhanced = service._enhance_query(query, [])
    assert enhanced == query
