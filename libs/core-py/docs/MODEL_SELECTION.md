# Model Selection and Benchmarking

## Overview

This document describes the model selection process and benchmarking results for the Aura ML workflows.

## Reasoning Models

### Recommended: GPT-4o-mini (Default)

**Why**:

- Cost-effective for high-volume usage
- Good performance for code analysis tasks
- Fast response times
- Sufficient reasoning capability for violation analysis and lesson generation

**Configuration**:

```bash
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7  # For creative lesson generation
```

### Alternative: GPT-4o

**When to Use**:

- Complex reasoning tasks
- High-stakes violation analysis
- When accuracy is more important than cost

**Configuration**:

```bash
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.3  # Lower temperature for analysis tasks
```

### Local Alternative: Llama 3 (via Ollama)

**When to Use**:

- Privacy-sensitive environments
- Offline operation
- Cost reduction for high-volume usage

**Configuration**:

```bash
LLM_MODEL=llama3
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

## Embedding Models

### Recommended: text-embedding-3-small (Default)

**Why**:

- Good balance of quality and cost
- Fast embedding generation
- Sufficient for code/documentation retrieval

**Configuration**:

```bash
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai
```

### Alternative: text-embedding-3-large

**When to Use**:

- Higher accuracy requirements
- Complex semantic queries
- When embedding quality is critical

### Local Alternative: sentence-transformers

**When to Use**:

- Privacy requirements
- Offline operation
- Cost reduction

**Configuration**:

```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_PROVIDER=local
```

## Benchmarking Results

### Reasoning Model Performance

| Model       | Speed  | Cost     | Quality   | Use Case             |
| ----------- | ------ | -------- | --------- | -------------------- |
| gpt-4o-mini | Fast   | Low      | Good      | Default, high volume |
| gpt-4o      | Medium | High     | Excellent | Complex reasoning    |
| llama3      | Slow   | Very Low | Good      | Privacy, offline     |

### Embedding Model Performance

| Model                  | Speed  | Cost     | Quality   | Dimensions |
| ---------------------- | ------ | -------- | --------- | ---------- |
| text-embedding-3-small | Fast   | Low      | Good      | 1536       |
| text-embedding-3-large | Medium | Medium   | Excellent | 3072       |
| all-MiniLM-L6-v2       | Fast   | Very Low | Good      | 384        |

## Configuration

Models are configured via environment variables:

```bash
# Reasoning Model
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_ENABLED=true

# Embedding Model
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai

# RAG Configuration
RAG_ENABLED=true
RAG_TOP_K=3
```

## Performance Considerations

1. **Latency**: GPT-4o-mini provides best latency for real-time workflows
2. **Cost**: Consider token usage and API costs for high-volume scenarios
3. **Quality**: Balance between model capability and requirements
4. **Privacy**: Use local models when data privacy is critical

## Future Optimization

- [ ] Benchmark with actual workload data
- [ ] A/B test different models
- [ ] Implement model fallback strategies
- [ ] Add performance monitoring
- [ ] Optimize prompt length for cost reduction
