"""
Chunking Strategies for RAG Pipeline

Provides configurable text chunking strategies for document ingestion.
Supports recursive, fixed-size, and semantic chunking approaches.
"""

import logging
from typing import Literal

from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from core_py.ml.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKING_STRATEGY,
)
from core_py.rag.exceptions import RAGValidationError

logger = logging.getLogger(__name__)


def get_text_splitter(
    strategy: Literal["fixed", "recursive", "semantic"] | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> CharacterTextSplitter | RecursiveCharacterTextSplitter:
    """
    Get a text splitter based on the specified strategy.

    Args:
        strategy: Chunking strategy to use. If None, uses CHUNKING_STRATEGY from config.
            - "recursive": RecursiveCharacterTextSplitter (respects code/markdown structure)
            - "fixed": CharacterTextSplitter (fixed-size chunks)
            - "semantic": Not yet implemented (raises NotImplementedError)
        chunk_size: Size of chunks in characters. If None, uses CHUNK_SIZE from config.
        chunk_overlap: Overlap between chunks in characters. If None, uses CHUNK_OVERLAP from config.

    Returns:
        Text splitter instance configured with the specified strategy.

    Raises:
        NotImplementedError: If semantic chunking is requested (not yet implemented)
        ValueError: If an invalid strategy is specified

    Example:
        >>> splitter = get_text_splitter("recursive")
        >>> chunks = splitter.split_text("Long text here...")
    """
    strategy = strategy or CHUNKING_STRATEGY
    chunk_size = chunk_size or CHUNK_SIZE
    chunk_overlap = chunk_overlap or CHUNK_OVERLAP

    # Input validation
    if chunk_size <= 0:
        raise RAGValidationError(f"chunk_size must be positive, got {chunk_size}")
    if chunk_overlap < 0:
        raise RAGValidationError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
    if chunk_overlap >= chunk_size:
        raise RAGValidationError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
        )

    if strategy == "recursive":
        logger.debug(
            "Using RecursiveCharacterTextSplitter",
            extra={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap},
        )
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",  # Paragraphs
                "\n",  # Lines
                ". ",  # Sentences
                " ",  # Words
                "",  # Characters
            ],
        )

    elif strategy == "fixed":
        logger.debug(
            "Using CharacterTextSplitter",
            extra={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap},
        )
        return CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="",
        )

    elif strategy == "semantic":
        raise NotImplementedError(
            "Semantic chunking is not yet implemented. "
            "Use 'recursive' or 'fixed' strategy instead."
        )

    else:
        raise ValueError(
            f"Invalid chunking strategy: {strategy}. "
            f"Supported strategies: 'recursive', 'fixed', 'semantic'"
        )


def chunk_text(
    text: str,
    strategy: Literal["fixed", "recursive", "semantic"] | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """
    Chunk text using the specified strategy.

    Convenience function that creates a splitter and chunks text in one call.

    Args:
        text: Text to chunk
        strategy: Chunking strategy (see get_text_splitter for details)
        chunk_size: Size of chunks in characters
        chunk_overlap: Overlap between chunks in characters

    Returns:
        List of text chunks

    Example:
        >>> chunks = chunk_text("Long text...", strategy="recursive")
        >>> len(chunks)
        5
    """
    splitter = get_text_splitter(
        strategy=strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)
