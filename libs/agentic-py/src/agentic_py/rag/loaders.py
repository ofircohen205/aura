"""
Document Loaders for RAG Pipeline

Provides loaders for different file types (markdown, Python, TypeScript, etc.)
with metadata extraction and content parsing.
"""

import ast
import logging
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from agentic_py.rag.exceptions import RAGFileError, RAGPathError
from agentic_py.rag.utils import validate_file_size, validate_path

logger = logging.getLogger(__name__)

# Try to import yaml for proper frontmatter parsing
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning(
        "pyyaml not installed. Frontmatter parsing will use simple string splitting. "
        "Install pyyaml for better YAML support: pip install pyyaml"
    )


def load_markdown(path: str | Path) -> Document:
    """
    Load a markdown file with frontmatter support.

    Extracts frontmatter (YAML between --- markers) if present and includes
    it in metadata. The main content is the markdown body.

    Args:
        path: Path to the markdown file

    Returns:
        Document with page_content (markdown text) and metadata

    Raises:
        RAGPathError: If path is invalid or outside allowed directories
        RAGFileError: If file cannot be read or exceeds size limit
        FileNotFoundError: If file doesn't exist

    Example:
        >>> doc = load_markdown("docs/guide.md")
        >>> doc.page_content  # Markdown content
        >>> doc.metadata["source"]  # File path
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")

    # Validate path and file size
    try:
        validated_path = validate_path(path)
        validate_file_size(validated_path)
    except RAGPathError:
        raise
    except RAGFileError:
        raise

    # Get file stat info once
    stat_info = validated_path.stat()

    try:
        content = validated_path.read_text(encoding="utf-8")
    except PermissionError as e:
        raise RAGFileError(f"Permission denied reading {validated_path}") from e
    except OSError as e:
        raise RAGFileError(f"Failed to read {validated_path}: {e}") from e

    metadata: dict[str, Any] = {
        "source": str(validated_path),
        "file_type": "markdown",
        "language": "markdown",
        "last_modified": stat_info.st_mtime,
        "file_size": stat_info.st_size,
    }

    # Extract frontmatter if present
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) == 3:
            frontmatter = parts[1]
            body = parts[2]

            # Use pyyaml if available, otherwise fall back to simple parsing
            if YAML_AVAILABLE:
                try:
                    frontmatter_data = yaml.safe_load(frontmatter)
                    if frontmatter_data and isinstance(frontmatter_data, dict):
                        metadata.update(frontmatter_data)
                except yaml.YAMLError as e:
                    logger.warning(f"Failed to parse YAML frontmatter in {validated_path}: {e}")
                    # Fall back to simple parsing
                    _parse_simple_frontmatter(frontmatter, metadata)
            else:
                _parse_simple_frontmatter(frontmatter, metadata)

            content = body

    return Document(page_content=content, metadata=metadata)


def _parse_simple_frontmatter(frontmatter: str, metadata: dict[str, Any]) -> None:
    """
    Parse simple frontmatter using basic string splitting.

    This is a fallback when pyyaml is not available. Only handles simple key: value pairs.

    Args:
        frontmatter: Frontmatter string to parse
        metadata: Metadata dict to update
    """
    for line in frontmatter.split("\n"):
        if ":" in line and not line.strip().startswith("#"):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"').strip("'")


def load_python(path: str | Path) -> Document:
    """
    Load a Python file with AST parsing for better structure understanding.

    Preserves code structure and can extract function/class names for metadata.

    Args:
        path: Path to the Python file

    Returns:
        Document with page_content (Python code) and metadata including
        function/class names if parseable

    Raises:
        RAGPathError: If path is invalid or outside allowed directories
        RAGFileError: If file cannot be read or exceeds size limit
        FileNotFoundError: If file doesn't exist

    Example:
        >>> doc = load_python("src/main.py")
        >>> doc.metadata.get("functions")  # List of function names
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Python file not found: {path}")

    # Validate path and file size
    try:
        validated_path = validate_path(path)
        validate_file_size(validated_path)
    except RAGPathError:
        raise
    except RAGFileError:
        raise

    # Get file stat info once
    stat_info = validated_path.stat()

    try:
        content = validated_path.read_text(encoding="utf-8")
    except PermissionError as e:
        raise RAGFileError(f"Permission denied reading {validated_path}") from e
    except OSError as e:
        raise RAGFileError(f"Failed to read {validated_path}: {e}") from e

    metadata: dict[str, Any] = {
        "source": str(validated_path),
        "file_type": "python",
        "language": "python",
        "last_modified": stat_info.st_mtime,
        "file_size": stat_info.st_size,
    }

    # Try to parse AST to extract structure
    try:
        tree = ast.parse(content)
        functions = []
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        if functions:
            metadata["functions"] = functions
        if classes:
            metadata["classes"] = classes
    except SyntaxError:
        # If file has syntax errors, just log and continue
        logger.warning(f"Could not parse Python AST for {validated_path}, using raw content")

    return Document(page_content=content, metadata=metadata)


def load_typescript(path: str | Path) -> Document:
    """
    Load a TypeScript or TSX file.

    Args:
        path: Path to the TypeScript file (.ts, .tsx)

    Returns:
        Document with page_content (TypeScript code) and metadata

    Raises:
        RAGPathError: If path is invalid or outside allowed directories
        RAGFileError: If file cannot be read or exceeds size limit
        FileNotFoundError: If file doesn't exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"TypeScript file not found: {path}")

    # Validate path and file size
    try:
        validated_path = validate_path(path)
        validate_file_size(validated_path)
    except RAGPathError:
        raise
    except RAGFileError:
        raise

    # Get file stat info once
    stat_info = validated_path.stat()

    try:
        content = validated_path.read_text(encoding="utf-8")
    except PermissionError as e:
        raise RAGFileError(f"Permission denied reading {validated_path}") from e
    except OSError as e:
        raise RAGFileError(f"Failed to read {validated_path}: {e}") from e

    file_type = "typescript"
    if validated_path.suffix == ".tsx":
        file_type = "tsx"

    metadata: dict[str, Any] = {
        "source": str(validated_path),
        "file_type": file_type,
        "language": "typescript",
        "last_modified": stat_info.st_mtime,
        "file_size": stat_info.st_size,
    }

    return Document(page_content=content, metadata=metadata)


def load_text(path: str | Path) -> Document:
    """
    Load a generic text file.

    Fallback loader for any text file that doesn't have a specific loader.

    Args:
        path: Path to the text file

    Returns:
        Document with page_content (text content) and metadata

    Raises:
        RAGPathError: If path is invalid or outside allowed directories
        RAGFileError: If file cannot be read or exceeds size limit
        FileNotFoundError: If file doesn't exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    # Validate path and file size
    try:
        validated_path = validate_path(path)
        validate_file_size(validated_path)
    except RAGPathError:
        raise
    except RAGFileError:
        raise

    # Get file stat info once
    stat_info = validated_path.stat()

    try:
        content = validated_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try with different encoding
        logger.warning(f"UTF-8 decode failed for {validated_path}, trying latin-1")
        try:
            content = validated_path.read_text(encoding="latin-1")
        except (PermissionError, OSError) as e:
            raise RAGFileError(f"Failed to read {validated_path}: {e}") from e
    except PermissionError as e:
        raise RAGFileError(f"Permission denied reading {validated_path}") from e
    except OSError as e:
        raise RAGFileError(f"Failed to read {validated_path}: {e}") from e

    metadata: dict[str, Any] = {
        "source": str(validated_path),
        "file_type": "text",
        "language": "text",
        "last_modified": stat_info.st_mtime,
        "file_size": stat_info.st_size,
    }

    return Document(page_content=content, metadata=metadata)


def load_document(path: str | Path) -> Document:
    """
    Load a document based on its file extension.

    Automatically selects the appropriate loader based on file extension.

    Args:
        path: Path to the file

    Returns:
        Document with page_content and metadata

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is not supported

    Supported extensions:
        - .md, .markdown -> MarkdownLoader
        - .py -> PythonLoader
        - .ts, .tsx -> TypeScriptLoader
        - Others -> GenericTextLoader

    Example:
        >>> doc = load_document("docs/guide.md")
        >>> doc = load_document("src/main.py")
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".md", ".markdown"):
        return load_markdown(path)
    elif suffix == ".py":
        return load_python(path)
    elif suffix in (".ts", ".tsx"):
        return load_typescript(path)
    else:
        # Try as generic text file
        logger.debug(f"Using generic text loader for {path}")
        return load_text(path)
