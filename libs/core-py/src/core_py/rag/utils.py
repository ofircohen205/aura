"""
RAG Pipeline Utilities

Helper functions for path validation, file operations, and common utilities.
"""

import asyncio
import logging
from pathlib import Path

from core_py.ml.config import RAG_ALLOWED_BASE_DIRS, RAG_MAX_FILE_SIZE
from core_py.rag.exceptions import RAGFileError, RAGPathError

logger = logging.getLogger(__name__)


def validate_path(path: str | Path, base_dirs: list[str] | None = None) -> Path:
    """
    Validate and resolve a file path, checking for path traversal attempts.

    Args:
        path: Path to validate
        base_dirs: List of allowed base directories. If None, uses RAG_ALLOWED_BASE_DIRS from config.
            If empty list, no restrictions (all paths allowed).

    Returns:
        Resolved Path object

    Raises:
        RAGPathError: If path is outside allowed directories or invalid

    Example:
        >>> validate_path("../sensitive/file.txt", base_dirs=["/allowed/dir"])
        RAGPathError: Path is outside allowed directory
    """
    path = Path(path)
    base_dirs = base_dirs if base_dirs is not None else RAG_ALLOWED_BASE_DIRS

    # Resolve the path to handle .. and symlinks
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as e:
        raise RAGPathError(f"Failed to resolve path {path}: {e}") from e

    # If no base directories specified, allow all paths (no restriction)
    if not base_dirs:
        return resolved

    # Check if path is within any allowed base directory
    is_allowed = False
    for base_dir_str in base_dirs:
        if not base_dir_str or not base_dir_str.strip():
            continue
        try:
            base_dir = Path(base_dir_str).resolve()
            # Use pathlib's is_relative_to if available (Python 3.9+), otherwise string comparison
            try:
                is_allowed = resolved.is_relative_to(base_dir)
            except AttributeError:
                # Fallback for Python < 3.9
                is_allowed = str(resolved).startswith(str(base_dir))
            if is_allowed:
                break
        except (OSError, RuntimeError) as e:
            logger.warning(f"Invalid base directory {base_dir_str}: {e}")
            continue

    if not is_allowed:
        raise RAGPathError(f"Path {resolved} is outside allowed directories. Allowed: {base_dirs}")

    return resolved


def validate_file_size(path: Path) -> None:
    """
    Validate that a file does not exceed the maximum allowed size.

    Args:
        path: Path to the file

    Raises:
        RAGFileError: If file exceeds maximum size
        FileNotFoundError: If file doesn't exist

    Example:
        >>> validate_file_size(Path("large_file.txt"))
        RAGFileError: File exceeds maximum size
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_size = path.stat().st_size
    if file_size > RAG_MAX_FILE_SIZE:
        raise RAGFileError(
            f"File {path} exceeds maximum size of {RAG_MAX_FILE_SIZE} bytes "
            f"(got {file_size} bytes). Increase RAG_MAX_FILE_SIZE if needed."
        )


async def read_file_async(path: Path, encoding: str = "utf-8") -> str:
    """
    Read a file asynchronously using asyncio.to_thread.

    Args:
        path: Path to the file
        encoding: File encoding (default: utf-8)

    Returns:
        File contents as string

    Raises:
        RAGFileError: If file reading fails
    """
    try:
        # Use asyncio.to_thread for async execution
        content = await asyncio.to_thread(path.read_text, encoding=encoding)
        return content
    except UnicodeDecodeError:
        # Try with different encoding
        logger.warning(f"UTF-8 decode failed for {path}, trying latin-1")
        try:
            content = await asyncio.to_thread(path.read_text, encoding="latin-1")
            return content
        except Exception as e2:
            raise RAGFileError(f"Failed to read file {path}: {e2}") from e2
    except (PermissionError, OSError) as e:
        raise RAGFileError(f"Failed to read file {path}: {e}") from e
