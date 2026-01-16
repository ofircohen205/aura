# RAG Pipeline Logging Guidelines

This document defines logging standards for the RAG pipeline modules.

## Logging Levels

### DEBUG

Use for detailed diagnostic information useful during development and troubleshooting:

- File discovery details
- Chunking strategy selection
- Vector store initialization steps
- Progress updates during batch processing
- Low-level operation details

**Example:**

```python
logger.debug("Using RecursiveCharacterTextSplitter", extra={"chunk_size": 1000})
```

### INFO

Use for general operational messages that confirm normal operation:

- Successful document ingestion
- Directory ingestion completion
- Vector store initialization success
- File discovery summary (count of files found)
- Batch processing completion

**Example:**

```python
logger.info("Document ingested successfully", extra={"path": str(path), "chunks": 5})
```

### WARNING

Use for recoverable issues that don't prevent operation:

- RAG service disabled
- YAML parsing fallback to simple parsing
- Missing optional dependencies (e.g., pyyaml)
- File size approaching limits
- Vector store not initialized (but operation can continue)

**Example:**

```python
logger.warning("pyyaml not installed. Frontmatter parsing will use simple string splitting.")
```

### ERROR

Use for failures that require attention but don't crash the application:

- File read failures
- Document ingestion failures (individual files)
- Vector store initialization failures
- Configuration errors

**Example:**

```python
logger.error("Failed to read file", extra={"path": str(path), "error": str(e)}, exc_info=True)
```

## Structured Logging

Always use the `extra={}` parameter for structured logging:

```python
logger.info(
    "Document ingested",
    extra={
        "path": str(path),
        "chunks": len(chunked_docs),
        "strategy": strategy,
        "file_size": stat_info.st_size,
    },
)
```

## Common Extra Fields

- `path`: File or directory path (as string)
- `chunks`: Number of chunks created
- `strategy`: Chunking strategy used
- `file_size`: File size in bytes
- `files_processed`: Number of files processed
- `total_chunks`: Total chunks created
- `errors`: Number of errors encountered
- `vector_store_type`: Type of vector store (pgvector/faiss)
- `error`: Error message
- `error_type`: Type of error (exception class name)

## Best Practices

1. **Always include context**: Use `extra={}` to provide structured data
2. **Use appropriate levels**: Don't log everything as ERROR
3. **Include exc_info=True**: For ERROR logs with exceptions
4. **Log at boundaries**: Log at function entry/exit for important operations
5. **Avoid sensitive data**: Don't log passwords, API keys, or full file contents
6. **Be consistent**: Use the same field names across modules

## Examples

### Good Logging

```python
logger.info(
    "Directory ingestion completed",
    extra={
        "directory": str(directory),
        "files_processed": files_processed,
        "total_chunks": len(all_documents),
        "errors": len(errors),
    },
)
```

### Bad Logging

```python
logger.info(f"Done processing {directory}")  # No structured data
logger.error("Error")  # No context, no exc_info
```
