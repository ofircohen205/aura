# Lesson Ingestion Guide

This document provides instructions for ingesting the educational lessons into the RAG vector database.

## Java Loader Verification

**Status: ✅ Not Required**

The educational lessons are stored as Markdown files with YAML frontmatter. The existing `load_markdown()` function in `libs/agentic-py/src/agentic_py/rag/loaders.py` already supports:

- YAML frontmatter extraction
- Metadata parsing (title, language, difficulty, prerequisites, keywords)
- Content extraction (markdown body)

Since all lessons (Python, TypeScript, and Java) are in Markdown format, no Java-specific loader is needed. The markdown loader handles all three languages correctly.

### Verification

The markdown loader extracts the following metadata from lesson frontmatter:

```yaml
---
title: "Lesson Title"
language: python|typescript|java
difficulty: beginner|intermediate|advanced
prerequisites: []
keywords: []
---
```

This metadata is automatically included in the vector store, enabling:

- Language-specific filtering
- Difficulty-based retrieval
- Keyword-based search
- Prerequisite tracking

## Ingestion Instructions

### Using the CLI

```bash
# Ingest all lessons
aura rag ingest docs/lessons/

# Ingest lessons for a specific language
aura rag ingest docs/lessons/python/
aura rag ingest docs/lessons/typescript/
aura rag ingest docs/lessons/java/

# Ingest lessons for a specific difficulty level
aura rag ingest docs/lessons/python/beginner/
```

### Using Python API

```python
from agentic_py.rag.service import RagService

service = RagService(enabled=True)

# Ingest all lessons
result = await service.ingest_directory("docs/lessons/")

print(f"Files processed: {result['files_processed']}")
print(f"Total chunks: {result['total_chunks']}")
```

### Using the Test Script

A test script is available at `scripts/test-lesson-ingestion.py` that:

1. Verifies the markdown loader works with lesson files
2. Ingests all lessons into RAG
3. Tests retrieval for each language
4. Tests retrieval with error patterns

```bash
python scripts/test-lesson-ingestion.py
```

## Expected Results

After ingestion, you should have:

- **90 lesson files** processed (30 Python + 30 TypeScript + 30 Java)
- **Multiple chunks per lesson** (depending on chunking strategy)
- **Metadata preserved** for each chunk (language, difficulty, keywords, etc.)

## Testing Retrieval

### Language-Specific Queries

```python
# Python query
context = await service.query_knowledge(
    "How do I create variables in Python?",
    top_k=3
)

# TypeScript query
context = await service.query_knowledge(
    "How do I declare variables with types in TypeScript?",
    top_k=3
)

# Java query
context = await service.query_knowledge(
    "How do I declare variables in Java?",
    top_k=3
)
```

### Error Pattern Queries

The RAG service can enhance queries with error patterns:

```python
# Python error patterns
context = await service.query_knowledge(
    "Help with errors",
    error_patterns=["NameError: name 'x' is not defined"],
    top_k=3
)

# TypeScript error patterns
context = await service.query_knowledge(
    "Type errors",
    error_patterns=["TypeError: Cannot read property"],
    top_k=3
)

# Java error patterns
context = await service.query_knowledge(
    "Null pointer exception",
    error_patterns=["NullPointerException"],
    top_k=3
)
```

## Integration with Struggle Detection

The lessons are automatically used by the struggle detection workflow when:

1. Error patterns match lesson keywords
2. Language is detected from code context
3. Difficulty level matches student's experience (if available)

The RAG service retrieves relevant lesson content which is then included in the lesson generation prompt.

## Troubleshooting

### Lessons Not Being Retrieved

1. Verify lessons were ingested: Check vector store for documents with `language` metadata
2. Check query relevance: Ensure queries match lesson keywords and content
3. Verify metadata: Check that frontmatter was parsed correctly

### Metadata Not Preserved

1. Ensure `pyyaml` is installed: `pip install pyyaml`
2. Check frontmatter format: Must start with `---\n` and have valid YAML
3. Review loader logs: Check for YAML parsing warnings

### Low Retrieval Quality

1. Adjust `top_k` parameter: Increase for more results
2. Enhance queries: Include more specific keywords
3. Review chunking strategy: May need to adjust chunk size/overlap
