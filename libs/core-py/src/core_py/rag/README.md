# RAG Pipeline Documentation

This module provides a complete Retrieval-Augmented Generation (RAG) pipeline for ingesting, storing, and querying knowledge from documentation and code files.

## Overview

The RAG pipeline consists of several components:

1. **Document Loaders** - Load files of different types (markdown, Python, TypeScript)
2. **Chunking Strategies** - Split documents into manageable chunks
3. **Ingestion Pipeline** - Process and ingest documents into vector stores
4. **RAG Service** - Query the vector store for relevant knowledge

## Vector Store Types

The pipeline supports two vector store backends:

- **pgvector** (Production): PostgreSQL extension for vector similarity search
- **FAISS** (Development): Local file-based vector store for testing

## Configuration

Set the following environment variables:

```bash
# Enable RAG
RAG_ENABLED=true

# Vector store type
VECTOR_STORE_TYPE=pgvector  # or "faiss"

# pgvector configuration
PGVECTOR_CONNECTION_STRING=postgresql://user:password@localhost:5432/aura
PGVECTOR_COLLECTION=aura_knowledge_base

# FAISS configuration
FAISS_INDEX_PATH=./faiss_index

# Chunking configuration
CHUNKING_STRATEGY=recursive  # or "fixed"
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Embedding model
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-api-key

# RAG Ingestion Configuration
RAG_MAX_FILE_SIZE=10485760  # 10MB default (in bytes)
RAG_INGESTION_BATCH_SIZE=100  # Documents per batch
RAG_ALLOWED_BASE_DIRS=/allowed/dir1,/allowed/dir2  # Comma-separated (empty = no restriction)
```

## Usage

### Using the CLI

The easiest way to ingest documents is using the CLI:

```bash
# Ingest a single file
aura rag ingest docs/guide.md

# Ingest a directory recursively
aura rag ingest docs/

# Ingest only markdown files
aura rag ingest docs/ --file-patterns "*.md"

# Dry run to see what would be ingested
aura rag ingest docs/ --dry-run
```

### Using Python API

```python
from core_py.rag.service import RagService

# Initialize service
service = RagService(enabled=True)

# Ingest a single document
await service.ingest_document("docs/guide.md")

# Ingest a directory
result = await service.ingest_directory(
    "docs/",
    file_patterns=["*.md", "*.py"],
    recursive=True
)

print(f"Processed {result['files_processed']} files")
print(f"Created {result['total_chunks']} chunks")

# Query the knowledge base
context = await service.query_knowledge(
    "How do I use the API?",
    error_patterns=["authentication", "endpoints"]
)
```

### Using Individual Components

```python
from core_py.rag.loaders import load_document
from core_py.rag.chunking import get_text_splitter

# Load a document
doc = load_document("docs/guide.md")

# Chunk it
splitter = get_text_splitter("recursive")
chunks = splitter.split_text(doc.page_content)
```

## Chunking Strategies

### Recursive (Recommended)

Respects document structure (paragraphs, lines, sentences). Best for:

- Markdown files
- Code files
- Structured documentation

```python
splitter = get_text_splitter("recursive", chunk_size=1000, chunk_overlap=200)
```

### Fixed

Fixed-size chunks with overlap. Best for:

- Plain text files
- When structure is not important

```python
splitter = get_text_splitter("fixed", chunk_size=1000, chunk_overlap=200)
```

### Semantic (Future)

Semantic chunking using embeddings. Not yet implemented.

## Document Loaders

### Markdown

Supports frontmatter extraction:

```markdown
---
title: Guide
author: Team
---

# Content

Body text.
```

### Python

Extracts function and class names from AST:

```python
doc = load_python("src/main.py")
print(doc.metadata["functions"])  # ['main', 'helper']
print(doc.metadata["classes"])   # ['MyClass']
```

### TypeScript

Loads `.ts` and `.tsx` files with metadata.

### Generic Text

Fallback for any text file.

## Database Setup

### pgvector Extension

The pgvector extension must be installed in PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This is handled automatically via Flyway migrations in the Docker setup.

## Integration with Workflows

The RAG service is already integrated with:

- **Struggle Detection Workflow** (`libs/core-py/src/core_py/workflows/struggle.py`)
- **Code Audit Workflow** (`libs/core-py/src/core_py/workflows/audit.py`)

These workflows automatically use `RagService.query_knowledge()` to retrieve relevant context.

## Testing

Run the test suite:

```bash
pytest libs/core-py/tests/test_rag_ingestion.py -v
pytest libs/core-py/tests/test_rag_service.py -v
```

## Security Considerations

### Path Traversal Protection

By default, all paths are allowed. To restrict file access:

```bash
RAG_ALLOWED_BASE_DIRS=/docs,/src
```

This ensures that only files within the specified directories can be ingested.

### File Size Limits

Files exceeding `RAG_MAX_FILE_SIZE` (default: 10MB) will be rejected to prevent DoS attacks. Adjust as needed:

```bash
RAG_MAX_FILE_SIZE=52428800  # 50MB
```

## Troubleshooting

### Vector Store Not Initialized

Ensure:

1. `RAG_ENABLED=true` is set
2. For pgvector: Extension is installed and connection string is correct
3. For FAISS: Directory exists and is writable

### No Results from Queries

1. Verify documents have been ingested
2. Check that embeddings are being generated (requires OpenAI API key)
3. Try increasing `RAG_TOP_K` to retrieve more results

### FAISS Placeholder Document

FAISS creates a placeholder document on first initialization. This is normal and will be replaced when you ingest real documents.

### Path Validation Errors

If you see `RAGPathError: Path is outside allowed directories`:

- Check `RAG_ALLOWED_BASE_DIRS` configuration
- Ensure paths are within allowed directories
- Set `RAG_ALLOWED_BASE_DIRS` to empty (or omit) to allow all paths

### File Size Errors

If you see `RAGFileError: File exceeds maximum size`:

- Increase `RAG_MAX_FILE_SIZE` if needed
- Or split large files into smaller chunks before ingestion

## Related Documentation

- [Chunking Strategy Guide](../docs/CHUNKING_STRATEGY.md)
- [ML Configuration](../ml/config.py)
- [Workflow Documentation](../workflows/)
