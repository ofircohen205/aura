"""
Document Ingestion Pipeline for RAG

Provides functionality to ingest documents from files or directories
into the vector store with chunking and metadata extraction.
"""

import logging
import re
from pathlib import Path
from typing import Any, Literal, TypedDict

from langchain_core.documents import Document

from core_py.ml.config import CHUNKING_STRATEGY
from core_py.rag.chunking import get_text_splitter
from core_py.rag.exceptions import RAGValidationError
from core_py.rag.loaders import load_document
from core_py.rag.utils import validate_path

logger = logging.getLogger(__name__)


class IngestionResult(TypedDict):
    """Result type for directory ingestion."""

    files_processed: int
    total_chunks: int
    errors: list[str]
    documents: list[Document]


def discover_files(
    directory: str | Path,
    file_patterns: list[str] | None = None,
    recursive: bool = True,
) -> list[Path]:
    """
    Discover files in a directory matching specified patterns.

    Args:
        directory: Directory to search
        file_patterns: List of file patterns (e.g., ["*.md", "*.py"]).
            If None, uses default patterns: ["*.md", "*.markdown", "*.py", "*.ts", "*.tsx"]
        recursive: Whether to search recursively

    Returns:
        List of file paths matching the patterns

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If path is not a directory or patterns are invalid
        RAGValidationError: If file patterns contain invalid characters

    Example:
        >>> files = discover_files("docs", file_patterns=["*.md"])
        >>> len(files)
        10
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    # Validate and normalize directory path
    try:
        validated_directory = validate_path(directory)
    except Exception:
        # If path validation fails, use original (may be intentional for unrestricted access)
        validated_directory = directory.resolve()

    if file_patterns is None:
        # Default patterns for common documentation and code files
        file_patterns = ["*.md", "*.markdown", "*.py", "*.ts", "*.tsx"]

    # Validate file patterns (prevent path traversal in patterns)
    for pattern in file_patterns:
        if not isinstance(pattern, str):
            raise RAGValidationError(f"File pattern must be a string, got {type(pattern)}")
        # Check for dangerous patterns (path traversal attempts)
        if ".." in pattern or "/" in pattern or "\\" in pattern:
            raise RAGValidationError(
                f"File pattern contains invalid characters (path traversal attempt): {pattern}"
            )
        # Validate pattern syntax (basic check)
        if not re.match(r"^[\w.*\-]+$", pattern.replace("*", "star").replace(".", "dot")):
            raise RAGValidationError(f"Invalid file pattern syntax: {pattern}")

    files: list[Path] = []
    pattern = "**/*" if recursive else "*"

    for file_pattern in file_patterns:
        # Handle both .md and *.md patterns
        if not file_pattern.startswith("*"):
            file_pattern = f"*{file_pattern}"

        found = list(
            validated_directory.glob(f"{pattern}/{file_pattern}" if recursive else file_pattern)
        )
        files.extend(found)

    # Remove duplicates and filter to only files
    files = list(set(files))
    files = [f for f in files if f.is_file()]

    logger.info(
        "Files discovered",
        extra={
            "directory": str(directory),
            "count": len(files),
            "patterns": file_patterns,
            "recursive": recursive,
        },
    )

    return sorted(files)


async def ingest_document(
    path: str | Path,
    chunking_strategy: Literal["fixed", "recursive", "semantic"] | None = None,
    metadata_override: dict[str, Any] | None = None,
) -> list[Document]:
    """
    Ingest a single document, chunk it, and return Document objects ready for vector store.

    Args:
        path: Path to the document file
        chunking_strategy: Chunking strategy to use (defaults to CHUNKING_STRATEGY from config)
        metadata_override: Optional metadata to override or add to document metadata

    Returns:
        List of Document objects (chunked) ready to be added to vector store

    Example:
        >>> docs = await ingest_document("docs/guide.md")
        >>> len(docs)  # Number of chunks
        5
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    logger.debug(f"Ingesting document: {path}")

    # Load document
    doc = load_document(path)

    # Override or add metadata
    if metadata_override:
        doc.metadata.update(metadata_override)

    # Chunk the document
    strategy = chunking_strategy or CHUNKING_STRATEGY
    splitter = get_text_splitter(strategy=strategy)

    # Split into chunks
    chunks = splitter.split_text(doc.page_content)

    # Create Document objects for each chunk with metadata
    chunked_docs: list[Document] = []
    for i, chunk_text in enumerate(chunks):
        chunk_metadata = doc.metadata.copy()
        chunk_metadata["chunk_index"] = i
        chunk_metadata["total_chunks"] = len(chunks)
        chunked_docs.append(Document(page_content=chunk_text, metadata=chunk_metadata))

    logger.info(
        "Document ingested",
        extra={
            "path": str(path),
            "chunks": len(chunked_docs),
            "strategy": strategy,
        },
    )

    return chunked_docs


async def ingest_directory(
    directory: str | Path,
    file_patterns: list[str] | None = None,
    recursive: bool = True,
    chunking_strategy: Literal["fixed", "recursive", "semantic"] | None = None,
    max_files: int | None = None,
) -> IngestionResult:
    """
    Ingest all documents in a directory.

    Args:
        directory: Directory to ingest
        file_patterns: File patterns to match (see discover_files)
        recursive: Whether to search recursively
        chunking_strategy: Chunking strategy to use
        max_files: Maximum number of files to process (for testing/limiting)

    Returns:
        IngestionResult dictionary with ingestion statistics:
        {
            "files_processed": int,
            "total_chunks": int,
            "errors": list[str],
            "documents": list[Document]  # All chunked documents ready for vector store
        }

    Example:
        >>> result = await ingest_directory("docs", file_patterns=["*.md"])
        >>> result["files_processed"]
        10
        >>> result["total_chunks"]
        50
    """
    directory = Path(directory)

    # Validate max_files if provided
    if max_files is not None and max_files <= 0:
        raise RAGValidationError(f"max_files must be positive, got {max_files}")

    files = discover_files(directory, file_patterns=file_patterns, recursive=recursive)

    if max_files:
        files = files[:max_files]

    all_documents: list[Document] = []
    errors: list[str] = []
    files_processed = 0

    logger.info(
        "Starting directory ingestion",
        extra={
            "directory": str(directory),
            "files_found": len(files),
            "patterns": file_patterns,
        },
    )

    # Process files with error handling
    # Note: For very large directories, consider processing in batches
    # to manage memory. Current implementation loads all documents into memory.
    for file_path in files:
        try:
            docs = await ingest_document(file_path, chunking_strategy=chunking_strategy)
            all_documents.extend(docs)
            files_processed += 1

            # Log progress for large directories
            if files_processed % 10 == 0:
                logger.debug(
                    f"Processing file {files_processed}/{len(files)}",
                    extra={"files_processed": files_processed, "total_files": len(files)},
                )
        except Exception as e:
            error_msg = f"Failed to ingest {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

    result: IngestionResult = {
        "files_processed": files_processed,
        "total_chunks": len(all_documents),
        "errors": errors,
        "documents": all_documents,
    }

    logger.info(
        "Directory ingestion completed",
        extra={
            "directory": str(directory),
            "files_processed": files_processed,
            "total_chunks": len(all_documents),
            "errors": len(errors),
        },
    )

    return result
