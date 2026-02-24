# RAG Pipeline Documentation

This document provides comprehensive documentation for the Retrieval-Augmented Generation (RAG) pipeline used in Aura for knowledge retrieval and context generation.

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Chunking Strategies](#chunking-strategies)
5. [Model Selection](#model-selection)
6. [Document Loaders](#document-loaders)
7. [Logging Guidelines](#logging-guidelines)
8. [Integration with Workflows](#integration-with-workflows)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)

## Overview

The RAG pipeline consists of several components:

1. **Document Loaders** - Load files of different types (markdown, Python, TypeScript)
2. **Chunking Strategies** - Split documents into manageable chunks
3. **Ingestion Pipeline** - Process and ingest documents into vector stores
4. **RAG Service** - Query the vector store for relevant knowledge

### Vector Store

The pipeline uses **pgvector** (PostgreSQL extension) for vector similarity search. This provides:

- ACID guarantees through PostgreSQL
- Single database for all data (no separate vector store)
- Production-ready with proper document management

## Configuration

Set the following environment variables:

```bash
# Enable RAG
RAG_ENABLED=true

# Vector store type (pgvector only)
VECTOR_STORE_TYPE=pgvector

# pgvector configuration
PGVECTOR_CONNECTION_STRING=postgresql://user:password@localhost:5432/aura
PGVECTOR_COLLECTION=aura_knowledge_base

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
from agentic_py.rag.service import RagService

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
from agentic_py.rag.loaders import load_document
from agentic_py.rag.chunking import get_text_splitter

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

**Pros:**

- Respects natural text boundaries
- Better semantic coherence
- Handles different document types well

**Cons:**

- More complex implementation
- Variable chunk sizes
- May create very small chunks

**Configuration:**

```python
splitter = get_text_splitter("recursive", chunk_size=1000, chunk_overlap=200)
```

Uses LangChain's `RecursiveCharacterTextSplitter` with separators: `\n\n`, `\n`, `. `, ` `, ``

### Fixed

Fixed-size chunks with overlap. Best for:

- Plain text files
- When structure is not important

**Pros:**

- Simple and predictable
- Fast processing
- Easy to implement

**Cons:**

- May split sentences/paragraphs mid-way
- Doesn't respect semantic boundaries
- May lose context

**Configuration:**

```python
splitter = get_text_splitter("fixed", chunk_size=1000, chunk_overlap=200)
```

### Semantic (Future)

Semantic chunking using embeddings. Not yet implemented.

**Pros:**

- Best semantic coherence
- Optimal for retrieval
- Context-aware splitting

**Cons:**

- Requires embedding model
- Slower processing
- More complex to implement

### Recommended Approach

**Current Recommendation**: Use **Recursive Character Chunking** as the default strategy.

**Rationale:**

1. Good balance between simplicity and quality
2. Works well with markdown and code documentation
3. Respects natural boundaries
4. No additional dependencies beyond LangChain

## Model Selection

### Reasoning Models

#### Recommended: GPT-4o-mini (Default)

**Why:**

- Cost-effective for high-volume usage
- Good performance for code analysis tasks
- Fast response times
- Sufficient reasoning capability for violation analysis and lesson generation

**Configuration:**

```bash
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7  # For creative lesson generation
```

#### Alternative: GPT-4o

**When to Use:**

- Complex reasoning tasks
- High-stakes violation analysis
- When accuracy is more important than cost

**Configuration:**

```bash
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.3  # Lower temperature for analysis tasks
```

#### Local Alternative: Llama 3 (via Ollama)

**When to Use:**

- Privacy-sensitive environments
- Offline operation
- Cost reduction for high-volume usage

**Configuration:**

```bash
LLM_MODEL=llama3
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Embedding Models

#### Recommended: text-embedding-3-small (Default)

**Why:**

- Good balance of quality and cost
- Fast embedding generation
- Sufficient for code/documentation retrieval

**Configuration:**

```bash
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai
```

#### Alternative: text-embedding-3-large

**When to Use:**

- Higher accuracy requirements
- Complex semantic queries
- When embedding quality is critical

#### Local Alternative: sentence-transformers

**When to Use:**

- Privacy requirements
- Offline operation
- Cost reduction

**Configuration:**

```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_PROVIDER=local
```

### Benchmarking Results

**Reasoning Model Performance:**

| Model       | Speed  | Cost     | Quality   | Use Case             |
| ----------- | ------ | -------- | --------- | -------------------- |
| gpt-4o-mini | Fast   | Low      | Good      | Default, high volume |
| gpt-4o      | Medium | High     | Excellent | Complex reasoning    |
| llama3      | Slow   | Very Low | Good      | Privacy, offline     |

**Embedding Model Performance:**

| Model                  | Speed  | Cost     | Quality   | Dimensions |
| ---------------------- | ------ | -------- | --------- | ---------- |
| text-embedding-3-small | Fast   | Low      | Good      | 1536       |
| text-embedding-3-large | Medium | Medium   | Excellent | 3072       |
| all-MiniLM-L6-v2       | Fast   | Very Low | Good      | 384        |

### Performance Considerations

1. **Latency**: GPT-4o-mini provides best latency for real-time workflows
2. **Cost**: Consider token usage and API costs for high-volume scenarios
3. **Quality**: Balance between model capability and requirements
4. **Privacy**: Use local models when data privacy is critical

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

The markdown loader automatically extracts YAML frontmatter metadata, which is particularly useful for educational lessons (see [Educational Lessons](#educational-lessons) section below).

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

## Educational Lessons

Aura includes a comprehensive set of 90 educational lessons covering Python, TypeScript, and Java programming languages. These lessons are designed to be ingested into the RAG vector database to support the struggle detection workflow's lesson generation capabilities.

### Lesson Structure

Lessons are located in `docs/lessons/` and organized by language and difficulty:

```
docs/lessons/
├── python/
│   ├── beginner/      (10 lessons)
│   ├── intermediate/  (10 lessons)
│   └── advanced/      (10 lessons)
├── typescript/
│   ├── beginner/      (10 lessons)
│   ├── intermediate/  (10 lessons)
│   └── advanced/      (10 lessons)
└── java/
    ├── beginner/      (10 lessons)
    ├── intermediate/  (10 lessons)
    └── advanced/      (10 lessons)
```

### Lesson Format

Each lesson is a Markdown file with YAML frontmatter containing metadata:

```markdown
---
title: "Variables and Data Types"
language: python
difficulty: beginner
prerequisites: []
keywords: [variables, data types, integers, floats, strings]
---

# Learning Objectives

...
```

The frontmatter includes:

- `title`: Lesson title
- `language`: `python`, `typescript`, or `java`
- `difficulty`: `beginner`, `intermediate`, or `advanced`
- `prerequisites`: List of prerequisite lesson titles
- `keywords`: List of relevant keywords for retrieval

### Ingesting Lessons

To ingest all educational lessons:

```bash
# Ingest all lessons
aura rag ingest docs/lessons/

# Ingest lessons for a specific language
aura rag ingest docs/lessons/python/
```

Or using the Python API:

```python
from agentic_py.rag.service import RagService

service = RagService(enabled=True)
result = await service.ingest_directory("docs/lessons/")
```

### Lesson Retrieval

The RAG service automatically retrieves relevant lessons based on:

1. **Error patterns**: Matches error messages to lesson keywords
2. **Language detection**: Filters lessons by programming language
3. **Difficulty level**: Can match student's experience level (if available)
4. **Query relevance**: Semantic similarity to lesson content

Example:

```python
# Query for Python variable errors
context = await service.query_knowledge(
    "Help with variable errors",
    error_patterns=["NameError: name 'x' is not defined"],
    top_k=3
)
```

The retrieved lesson content is then used by the struggle detection workflow to generate personalized lesson recommendations.

### Integration with Struggle Detection

The struggle detection workflow (`libs/agentic-py/src/agentic_py/workflows/struggle.py`) automatically uses lesson content when:

- Error patterns match lesson keywords
- Edit frequency indicates struggle
- Language can be detected from context

The workflow queries the RAG service and includes relevant lesson excerpts in the lesson generation prompt, enabling context-aware, personalized lesson recommendations.

### Documentation

For more details, see:

- [Lesson README](lessons/README.md) - Lesson format and structure
- [Lesson Index](lessons/INDEX.md) - Complete lesson catalog
- [Ingestion Guide](lessons/INGESTION.md) - Detailed ingestion instructions

## Logging Guidelines

### Logging Levels

#### DEBUG

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

#### INFO

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

#### WARNING

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

#### ERROR

Use for failures that require attention but don't crash the application:

- File read failures
- Document ingestion failures (individual files)
- Vector store initialization failures
- Configuration errors

**Example:**

```python
logger.error("Failed to read file", extra={"path": str(path), "error": str(e)}, exc_info=True)
```

### Structured Logging

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

### Common Extra Fields

- `path`: File or directory path (as string)
- `chunks`: Number of chunks created
- `strategy`: Chunking strategy used
- `file_size`: File size in bytes
- `files_processed`: Number of files processed
- `total_chunks`: Total chunks created
- `errors`: Number of errors encountered
- `vector_store_type`: Type of vector store (pgvector)
- `error`: Error message
- `error_type`: Type of error (exception class name)

### Best Practices

1. **Always include context**: Use `extra={}` to provide structured data
2. **Use appropriate levels**: Don't log everything as ERROR
3. **Include exc_info=True**: For ERROR logs with exceptions
4. **Log at boundaries**: Log at function entry/exit for important operations
5. **Avoid sensitive data**: Don't log passwords, API keys, or full file contents
6. **Be consistent**: Use the same field names across modules

## Integration with Workflows

The RAG service is already integrated with:

- **Struggle Detection Workflow** (`libs/agentic-py/src/agentic_py/workflows/struggle.py`)
- **Code Audit Workflow** (`libs/agentic-py/src/agentic_py/workflows/audit.py`)

These workflows automatically use `RagService.query_knowledge()` to retrieve relevant context.

## Database Setup

### pgvector Extension

The pgvector extension must be installed in PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This is handled automatically via Flyway migrations in the Docker setup.

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
2. pgvector extension is installed in PostgreSQL
3. Connection string is correct (`PGVECTOR_CONNECTION_STRING`)

### No Results from Queries

1. Verify documents have been ingested
2. Check that embeddings are being generated (requires OpenAI API key)
3. Try increasing `RAG_TOP_K` to retrieve more results

### Path Validation Errors

If you see `RAGPathError: Path is outside allowed directories`:

- Check `RAG_ALLOWED_BASE_DIRS` configuration
- Ensure paths are within allowed directories
- Set `RAG_ALLOWED_BASE_DIRS` to empty (or omit) to allow all paths

### File Size Errors

If you see `RAGFileError: File exceeds maximum size`:

- Increase `RAG_MAX_FILE_SIZE` if needed
- Or split large files into smaller chunks before ingestion

## Testing

Run the test suite:

```bash
pytest libs/agentic-py/tests/test_rag_ingestion.py -v
pytest libs/agentic-py/tests/test_rag_service.py -v
```

## Related Documentation

- [Development Guide](DEVELOPMENT.md) - Local development setup
- [Architecture Guide](ARCHITECTURE.md) - System architecture overview
- [User Guide](USER_GUIDE.md) - API and workflow usage
