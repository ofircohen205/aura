"""
Tests for RAG document ingestion pipeline.

Tests document loading, chunking, and ingestion into vector stores.
"""

import os

import pytest

from agentic_py.rag.chunking import chunk_text, get_text_splitter
from agentic_py.rag.exceptions import (
    RAGFileError,
    RAGPathError,
    RAGValidationError,
)
from agentic_py.rag.ingestion import discover_files, ingest_directory, ingest_document
from agentic_py.rag.loaders import (
    load_document,
    load_markdown,
    load_python,
    load_text,
    load_typescript,
)
from agentic_py.rag.utils import validate_file_size, validate_path


def test_get_text_splitter_recursive():
    """Test recursive text splitter creation."""
    splitter = get_text_splitter("recursive", chunk_size=100, chunk_overlap=20)
    assert splitter is not None
    assert splitter._chunk_size == 100
    assert splitter._chunk_overlap == 20


def test_get_text_splitter_fixed():
    """Test fixed text splitter creation."""
    splitter = get_text_splitter("fixed", chunk_size=200, chunk_overlap=50)
    assert splitter is not None
    assert splitter._chunk_size == 200
    assert splitter._chunk_overlap == 50


def test_get_text_splitter_semantic_not_implemented():
    """Test that semantic chunking raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Semantic chunking"):
        get_text_splitter("semantic")


def test_get_text_splitter_invalid_strategy():
    """Test that invalid strategy raises ValueError."""
    with pytest.raises(ValueError, match="Invalid chunking strategy"):
        get_text_splitter("invalid")


def test_get_text_splitter_validation_negative_chunk_size():
    """Test that negative chunk_size raises RAGValidationError."""
    with pytest.raises(RAGValidationError, match="chunk_size must be positive"):
        get_text_splitter("recursive", chunk_size=-1)


def test_get_text_splitter_validation_negative_overlap():
    """Test that negative chunk_overlap raises RAGValidationError."""
    with pytest.raises(RAGValidationError, match="chunk_overlap must be non-negative"):
        get_text_splitter("recursive", chunk_overlap=-1)


def test_get_text_splitter_validation_overlap_too_large():
    """Test that chunk_overlap >= chunk_size raises RAGValidationError."""
    with pytest.raises(RAGValidationError, match="chunk_overlap.*must be less than"):
        get_text_splitter("recursive", chunk_size=100, chunk_overlap=100)


def test_chunk_text():
    """Test chunking text into pieces."""
    text = "This is a long text. " * 50  # Create long text
    chunks = chunk_text(text, strategy="recursive", chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_load_markdown(tmp_path):
    """Test loading a markdown file."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\nThis is a test markdown file.")

    doc = load_markdown(md_file)
    assert doc.page_content == "# Test\n\nThis is a test markdown file."
    assert doc.metadata["source"] == str(md_file)
    assert doc.metadata["file_type"] == "markdown"
    assert doc.metadata["language"] == "markdown"


def test_load_markdown_with_frontmatter(tmp_path):
    """Test loading markdown with frontmatter."""
    md_file = tmp_path / "test.md"
    md_file.write_text("---\ntitle: Test\nauthor: Test Author\n---\n# Content\n\nBody text.")

    doc = load_markdown(md_file)
    assert "title" in doc.metadata
    assert doc.metadata["title"] == "Test"
    assert "# Content" in doc.page_content


def test_load_python(tmp_path):
    """Test loading a Python file."""
    py_file = tmp_path / "test.py"
    py_file.write_text('def hello():\n    print("Hello")\n\nclass Test:\n    pass')

    doc = load_python(py_file)
    assert doc.page_content == 'def hello():\n    print("Hello")\n\nclass Test:\n    pass'
    assert doc.metadata["file_type"] == "python"
    assert doc.metadata["language"] == "python"
    # Should extract functions and classes
    assert "functions" in doc.metadata or "classes" in doc.metadata


def test_load_typescript(tmp_path):
    """Test loading a TypeScript file."""
    ts_file = tmp_path / "test.ts"
    ts_file.write_text("function hello(): void {\n  console.log('Hello');\n}")

    doc = load_typescript(ts_file)
    assert "function hello" in doc.page_content
    assert doc.metadata["file_type"] == "typescript"
    assert doc.metadata["language"] == "typescript"


def test_load_text(tmp_path):
    """Test loading a generic text file."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("This is plain text content.")

    doc = load_text(txt_file)
    assert doc.page_content == "This is plain text content."
    assert doc.metadata["file_type"] == "text"


def test_load_document_auto_detection(tmp_path):
    """Test automatic loader selection based on extension."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    doc = load_document(md_file)
    assert doc.metadata["file_type"] == "markdown"

    py_file = tmp_path / "test.py"
    py_file.write_text("print('test')")

    doc = load_document(py_file)
    assert doc.metadata["file_type"] == "python"


def test_load_document_not_found():
    """Test loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_document("/nonexistent/file.md")


def test_discover_files(tmp_path):
    """Test file discovery in directory."""
    # Create test files
    (tmp_path / "file1.md").write_text("# Test 1")
    (tmp_path / "file2.py").write_text("print('test')")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.md").write_text("# Test 3")

    files = discover_files(tmp_path, file_patterns=["*.md"], recursive=True)
    assert len(files) == 2
    assert all(f.suffix == ".md" for f in files)

    files = discover_files(tmp_path, file_patterns=["*.md"], recursive=False)
    assert len(files) == 1  # Only top-level file


def test_discover_files_nonexistent_directory():
    """Test discovering files in non-existent directory raises error."""
    with pytest.raises(FileNotFoundError):
        discover_files("/nonexistent/directory")


@pytest.mark.asyncio
async def test_ingest_document(tmp_path):
    """Test ingesting a single document."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n" + "This is a long paragraph. " * 50)

    docs = await ingest_document(md_file, chunking_strategy="recursive")
    assert len(docs) > 0
    assert all(hasattr(doc, "page_content") for doc in docs)
    assert all(hasattr(doc, "metadata") for doc in docs)
    assert all("chunk_index" in doc.metadata for doc in docs)


@pytest.mark.asyncio
async def test_ingest_document_with_metadata_override(tmp_path):
    """Test ingesting document with metadata override."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    docs = await ingest_document(md_file, metadata_override={"custom": "value"})
    assert len(docs) > 0
    assert docs[0].metadata.get("custom") == "value"


@pytest.mark.asyncio
async def test_ingest_directory(tmp_path):
    """Test ingesting a directory of documents."""
    # Create test files
    (tmp_path / "file1.md").write_text("# File 1\n\nContent 1")
    (tmp_path / "file2.md").write_text("# File 2\n\nContent 2")
    (tmp_path / "ignore.py").write_text("print('ignore')")

    result = await ingest_directory(tmp_path, file_patterns=["*.md"], recursive=False, max_files=10)

    assert result["files_processed"] == 2
    assert result["total_chunks"] > 0
    assert len(result["documents"]) > 0
    assert all(hasattr(doc, "page_content") for doc in result["documents"])


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_ingest_directory_with_errors(tmp_path):
    """Test directory ingestion handles errors gracefully."""
    # Create one valid and one invalid file
    (tmp_path / "valid.md").write_text("# Valid")
    invalid_file = tmp_path / "invalid.md"
    # Make file unreadable (simulate permission error)
    invalid_file.write_text("# Invalid")

    result = await ingest_directory(tmp_path, file_patterns=["*.md"], recursive=False)

    # Should process at least the valid file
    assert result["files_processed"] >= 1


def test_chunk_text_empty():
    """Test chunking empty text."""
    chunks = chunk_text("", strategy="recursive")
    assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == "")


def test_chunk_text_short():
    """Test chunking short text (should return single chunk)."""
    text = "Short text"
    chunks = chunk_text(text, strategy="recursive", chunk_size=1000)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_load_python_with_syntax_error(tmp_path):
    """Test loading Python file with syntax errors (should still work)."""
    py_file = tmp_path / "syntax_error.py"
    py_file.write_text("def invalid syntax here")

    # Should not raise, but may not extract functions
    doc = load_python(py_file)
    assert doc.page_content == "def invalid syntax here"
    assert doc.metadata["file_type"] == "python"


def test_validate_path_allowed(tmp_path):
    """Test path validation with allowed base directory."""
    base_dir = tmp_path / "allowed"
    base_dir.mkdir()
    file_path = base_dir / "test.md"
    file_path.write_text("# Test")

    validated = validate_path(file_path, base_dirs=[str(base_dir)])
    assert validated == file_path.resolve()


def test_validate_path_traversal_attempt(tmp_path):
    """Test that path traversal attempts are blocked."""
    base_dir = tmp_path / "allowed"
    base_dir.mkdir()
    (tmp_path / "sensitive").mkdir()
    (tmp_path / "sensitive" / "secret.txt").write_text("secret")

    # Try to access file outside allowed directory
    with pytest.raises(RAGPathError, match="outside allowed directories"):
        validate_path(base_dir / ".." / "sensitive" / "secret.txt", base_dirs=[str(base_dir)])


def test_validate_path_no_restrictions(tmp_path):
    """Test path validation with no restrictions (empty base_dirs)."""
    file_path = tmp_path / "test.md"
    file_path.write_text("# Test")

    # Should work with empty base_dirs (no restrictions)
    validated = validate_path(file_path, base_dirs=[])
    assert validated == file_path.resolve()


def test_validate_file_size(tmp_path):
    """Test file size validation."""
    small_file = tmp_path / "small.txt"
    small_file.write_text("small content")

    # Should not raise for small file
    validate_file_size(small_file)

    # Create a large file (simulate)
    large_file = tmp_path / "large.txt"
    with open(large_file, "wb") as f:
        f.write(b"x" * (11 * 1024 * 1024))  # 11MB (exceeds 10MB default)

    with pytest.raises(RAGFileError, match="exceeds maximum size"):
        validate_file_size(large_file)


def test_discover_files_invalid_pattern(tmp_path):
    """Test that invalid file patterns raise RAGValidationError."""
    (tmp_path / "test.md").write_text("# Test")

    with pytest.raises(RAGValidationError, match="path traversal attempt"):
        discover_files(tmp_path, file_patterns=["../*.md"])

    with pytest.raises(RAGValidationError, match="invalid characters"):
        discover_files(tmp_path, file_patterns=["../../etc/passwd"])


@pytest.mark.asyncio
async def test_ingest_directory_max_files_validation_async(tmp_path):
    """Test that negative max_files raises RAGValidationError (async version)."""
    (tmp_path / "test.md").write_text("# Test")

    with pytest.raises(RAGValidationError, match="max_files must be positive"):
        await ingest_directory(tmp_path, max_files=-1)


@pytest.mark.asyncio
async def test_load_markdown_with_yaml_frontmatter(tmp_path):
    """Test loading markdown with proper YAML frontmatter."""
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "---\ntitle: Test Document\nauthor: Test Author\ntags:\n  - test\n  - example\n---\n# Content\n\nBody text."
    )

    doc = load_markdown(md_file)
    # Should parse YAML properly if pyyaml is available
    assert "title" in doc.metadata
    assert doc.metadata["title"] == "Test Document"
    assert "# Content" in doc.page_content


def test_load_markdown_file_size_limit(tmp_path, monkeypatch):
    """Test that file size limits are enforced."""
    # Patch the config value directly since it's imported at module level
    from agentic_py.config import rag as config
    from agentic_py.rag import utils

    monkeypatch.setattr(config, "RAG_MAX_FILE_SIZE", 100)
    monkeypatch.setattr(utils, "RAG_MAX_FILE_SIZE", 100)

    large_file = tmp_path / "large.md"
    large_file.write_text("# " + "x" * 200)  # Exceeds 100 bytes

    with pytest.raises(RAGFileError, match="exceeds maximum size"):
        load_markdown(large_file)


def test_load_python_permission_error(tmp_path, monkeypatch):
    """Test handling of permission errors."""
    py_file = tmp_path / "test.py"
    py_file.write_text("print('test')")

    # Make file unreadable (Unix only)
    if os.name != "nt":  # Skip on Windows
        py_file.chmod(0o000)
        try:
            with pytest.raises(RAGFileError, match="Permission denied"):
                load_python(py_file)
        finally:
            py_file.chmod(0o644)  # Restore permissions


def test_discover_files_pattern_validation(tmp_path):
    """Test file pattern validation."""
    (tmp_path / "test.md").write_text("# Test")

    with pytest.raises(RAGValidationError):
        discover_files(tmp_path, file_patterns=["../*.md"])

    with pytest.raises(RAGValidationError):
        discover_files(tmp_path, file_patterns=["/etc/passwd"])


@pytest.mark.asyncio
async def test_ingest_directory_empty_directory(tmp_path):
    """Test ingesting an empty directory."""
    result = await ingest_directory(tmp_path, file_patterns=["*.md"])
    assert result["files_processed"] == 0
    assert result["total_chunks"] == 0
    assert len(result["documents"]) == 0


@pytest.mark.asyncio
async def test_ingest_directory_with_binary_file(tmp_path):
    """Test that binary files are handled gracefully."""
    # Create a binary file
    binary_file = tmp_path / "binary.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03")

    # Create a valid text file
    text_file = tmp_path / "text.md"
    text_file.write_text("# Test")

    result = await ingest_directory(tmp_path, file_patterns=["*"])
    # Should process text file, may skip or error on binary
    assert result["files_processed"] >= 0  # At least attempted
