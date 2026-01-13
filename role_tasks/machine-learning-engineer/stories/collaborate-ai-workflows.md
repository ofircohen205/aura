# Story: Collaborate on LangGraph Workflows and RAG Pipeline

**Role:** Machine Learning Engineer
**Related SRS Section:** 4.1

## Desired Feature

While the Senior SWE builds the scaffolding (FastAPI, Class structures), the ML Engineer is responsible for the *intelligence* within. This involves designing the prompt chains, selecting optimal embedding models, and tuning the retrieval strategy for the RAG pipeline.

## Planning & Technical Spec

### AI Architecture

- **Models**:
  - Reasoning: GPT-4o or Claude 3.5 Sonnet (via API).
  - Local Fallback: Llama 3 (via Ollama).
  - Embeddings: OpenAI `text-embedding-3-small` or HuggingFace `all-MiniLM-L6-v2`.
- **Prompts**:
  - System prompts for "Architect Role".
  - Few-shot examples for "Golden Path" violations.

### Implementation Checklist

- [ ] Design Prompt Templates (Jinja2 or LangChain format).
- [ ] Optimize `generate_lesson` node: Ensure it answers the *specific* struggle, not generic advice.
- [ ] Optimize `check_violations` node: Tune sensitivity to reduce false positives (SRS 3.3).
- [ ] Evaluate Vector Store chunking strategy (semantic chunking vs fixed size).

## Testing Plan

- **Automated Tests**:
  - [ ] Eval pipeline (using `DeepEval` or custom): Feed 50 known "bad code" snippets and measure detection rate.
- **Manual Verification**:
  - [ ] Manual "Red Teaming": Try to trick the agent with edge cases.
