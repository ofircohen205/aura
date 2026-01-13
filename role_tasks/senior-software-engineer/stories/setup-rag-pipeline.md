# Story: Set up RAG Pipeline for "Golden Path" Documentation

**Role:** Senior Software Engineer (Collaborating with ML Engineer)
**Related SRS Section:** 1, 2.1, 4.1

## Desired Feature
To provide accurate architectural advice, the system needs to "read" and "index" the codebase and documentation. This RAG (Retrieval-Augmented Generation) pipeline will ingest markdown files, code snippets, and "Golden Path" examples into a vector store (ChromaDB for local, Qdrant for prod).

## Planning & Technical Spec

### Architecture
- **Vector Store**: ChromaDB (dev/local).
- **Embedding Model**: `text-embedding-3-small` (OpenAI) or local `sentence-transformers` (via Ollama).
- **Ingestion Pipeline**:
    - Directory walker to find `.md`, `.py`, `.ts` files.
    - Chunker (RecursiveCharacterTextSplitter) to break content into meaningful pieces.
    - Metadata extraction (filename, last modified, component type).

### Implementation Checklist
- [ ] Set up ChromaDB client/container.
- [ ] Create `RagService` class.
- [ ] Implement `ingest_document(path: str)` method.
- [ ] Implement `query_knowledge(query: str, filters: dict)` method.
- [ ] Create a CLI management command `aura-admin ingest <path>`.

## Testing Plan
- **Automated Tests**:
    - [ ] Test ingestion of a sample markdown file.
    - [ ] Test retrieval: Query "database" and ensure the sample file is returned in top-k results.
- **Manual Verification**:
    - [ ] Run ingestion on the `docs/` folder.
    - [ ] Query for a known concept via python shell and verify relevance.
