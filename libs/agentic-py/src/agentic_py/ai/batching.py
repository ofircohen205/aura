"""
LLM Call Batching

Provides batching functionality for multiple LLM calls to improve efficiency
and reduce costs when processing multiple similar requests.
"""

import asyncio
import logging
from typing import Any

from agentic_py.ai.llm import invoke_llm_with_retry
from agentic_py.config.llm import LLM_BATCH_DELAY, LLM_BATCH_SIZE

logger = logging.getLogger(__name__)

BATCH_SIZE = LLM_BATCH_SIZE
BATCH_DELAY = LLM_BATCH_DELAY


async def batch_llm_calls(
    prompts: list[str],
    batch_size: int | None = None,
    delay_between_batches: float | None = None,
) -> list[str]:
    """
    Process multiple LLM calls in batches.

    Args:
        prompts: List of prompts to process
        batch_size: Number of prompts to process concurrently per batch
        delay_between_batches: Delay in seconds between batches

    Returns:
        List of responses in the same order as prompts

    Example:
        >>> prompts = ["Analyze error 1", "Analyze error 2", "Analyze error 3"]
        >>> responses = await batch_llm_calls(prompts, batch_size=2)
        >>> # Processes first 2 concurrently, then the third
    """
    if not prompts:
        return []

    batch_size = batch_size or BATCH_SIZE
    delay = delay_between_batches or BATCH_DELAY

    results: list[str] = []

    for i in range(0, len(prompts), batch_size):
        batch = prompts[i : i + batch_size]
        logger.debug(
            f"Processing LLM batch {i // batch_size + 1}, size: {len(batch)}",
            extra={"batch_start": i, "batch_end": i + len(batch), "total_prompts": len(prompts)},
        )

        batch_results = await asyncio.gather(
            *[invoke_llm_with_retry(prompt) for prompt in batch],
            return_exceptions=True,
        )

        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(
                    f"LLM call failed in batch: {result}",
                    extra={"prompt_index": i + j, "error_type": type(result).__name__},
                    exc_info=True,
                )
                results.append(f"Error processing request: {type(result).__name__}")
            else:
                results.append(str(result))

        if i + batch_size < len(prompts) and delay > 0:
            await asyncio.sleep(delay)

    logger.info(
        f"Completed batch processing: {len(results)}/{len(prompts)} successful",
        extra={
            "total_prompts": len(prompts),
            "successful": sum(1 for r in results if not r.startswith("Error")),
        },
    )

    return results


async def batch_analyze_violations(
    violations: list[dict[str, Any]],
    analysis_prompt_template: str,
) -> list[dict[str, Any]]:
    """
    Batch analyze multiple violations using LLM.

    This function groups similar violations and analyzes them in batches
    to reduce LLM API calls and costs.

    Args:
        violations: List of violation dictionaries to analyze
        analysis_prompt_template: Template function that takes a violation and returns a prompt

    Returns:
        List of analyzed violations with analysis results added
    """
    if not violations:
        return []

    prompts = []
    for violation in violations:
        if callable(analysis_prompt_template):
            prompt = analysis_prompt_template(violation)
        else:
            prompt = analysis_prompt_template.format(**violation)
        prompts.append(prompt)

    responses = await batch_llm_calls(prompts)

    analyzed_violations = []
    for violation, response in zip(violations, responses, strict=False):
        analyzed = violation.copy()
        analyzed["llm_analysis"] = response
        analyzed_violations.append(analyzed)

    return analyzed_violations
