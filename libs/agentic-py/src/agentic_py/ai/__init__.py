"""
AI Infrastructure Module

Provides AI/LLM infrastructure including client utilities, caching, batching, and evaluation.
Renamed from ml/ to better reflect its purpose (AI/LLM infrastructure, not traditional ML).
"""

from agentic_py.ai.batching import batch_analyze_violations, batch_llm_calls
from agentic_py.ai.cache import (
    clear_cache,
    get_cache_stats,
    get_cached_response,
    set_cached_response,
)
from agentic_py.ai.evaluation import evaluate_rag_retrieval, evaluate_workflow_performance
from agentic_py.ai.llm import get_llm_client, invoke_llm_with_retry

__all__ = [
    # LLM
    "get_llm_client",
    "invoke_llm_with_retry",
    # Caching
    "get_cached_response",
    "set_cached_response",
    "clear_cache",
    "get_cache_stats",
    # Batching
    "batch_llm_calls",
    "batch_analyze_violations",
    # Evaluation
    "evaluate_rag_retrieval",
    "evaluate_workflow_performance",
]
