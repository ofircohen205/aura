# Chunking Strategy Evaluation

## Overview

This document describes the evaluation of different chunking strategies for the RAG pipeline vector store.

## Chunking Strategies

### 1. Fixed Size Chunking

**Description**: Splits text into fixed-size chunks with optional overlap.

**Pros**:

- Simple and predictable
- Fast processing
- Easy to implement

**Cons**:

- May split sentences/paragraphs mid-way
- Doesn't respect semantic boundaries
- May lose context

**Configuration**:

- `CHUNK_SIZE`: 1000 characters (default)
- `CHUNK_OVERLAP`: 200 characters (default)

### 2. Recursive Character Chunking

**Description**: Recursively splits text using separators (paragraphs, sentences, words).

**Pros**:

- Respects natural text boundaries
- Better semantic coherence
- Handles different document types well

**Cons**:

- More complex implementation
- Variable chunk sizes
- May create very small chunks

**Configuration**:

- Uses LangChain's `RecursiveCharacterTextSplitter`
- Separators: `\n\n`, `\n`, `. `, ` `, ``

### 3. Semantic Chunking

**Description**: Uses embeddings to create semantically coherent chunks.

**Pros**:

- Best semantic coherence
- Optimal for retrieval
- Context-aware splitting

**Cons**:

- Requires embedding model
- Slower processing
- More complex to implement

**Configuration**:

- Uses embedding similarity to determine split points
- Requires `EMBEDDING_MODEL` to be configured

## Recommended Approach

**Current Recommendation**: Use **Recursive Character Chunking** as the default strategy.

**Rationale**:

1. Good balance between simplicity and quality
2. Works well with markdown and code documentation
3. Respects natural boundaries
4. No additional dependencies beyond LangChain

**Future Optimization**: Once RAG pipeline is fully implemented (AURA-7), evaluate semantic chunking for improved retrieval quality.

## Implementation Status

- [x] Configuration support for all strategies
- [ ] Fixed size chunking implementation
- [ ] Recursive character chunking implementation
- [ ] Semantic chunking implementation
- [ ] Evaluation pipeline for comparing strategies
- [ ] Performance benchmarking

## Evaluation Metrics

When evaluating chunking strategies, consider:

1. **Chunk Quality**:
   - Semantic coherence
   - Size distribution
   - Boundary preservation

2. **Retrieval Performance**:
   - Precision@K
   - Recall@K
   - Mean Reciprocal Rank (MRR)

3. **Processing Performance**:
   - Chunking speed
   - Memory usage
   - Storage requirements

## Next Steps

1. Implement chunking strategies in RAG service (AURA-7)
2. Create evaluation dataset with known queries
3. Run comparative evaluation
4. Document optimal configuration
