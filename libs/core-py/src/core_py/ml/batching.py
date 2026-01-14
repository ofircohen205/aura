"""
LLM Call Batching

Provides batching functionality for multiple LLM calls to improve efficiency
and reduce costs when processing multiple similar requests.
"""

import asyncio
import logging
from typing import Any

from core_py.ml.config import LLM_BATCH_DELAY, LLM_BATCH_SIZE
from core_py.ml.llm import invoke_llm_with_retry

logger = logging.getLogger(__name__)

# Batching configuration (imported from config for consistency)
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

    # Process prompts in batches
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i : i + batch_size]
        logger.debug(
            f"Processing LLM batch {i // batch_size + 1}, size: {len(batch)}",
            extra={"batch_start": i, "batch_end": i + len(batch), "total_prompts": len(prompts)},
        )

        # Process batch concurrently
        batch_results = await asyncio.gather(
            *[invoke_llm_with_retry(prompt) for prompt in batch],
            return_exceptions=True,
        )

        # Handle results and exceptions
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(
                    f"LLM call failed in batch: {result}",
                    extra={"prompt_index": i + j, "error_type": type(result).__name__},
                    exc_info=True,
                )
                # Return error message as fallback
                results.append(f"Error processing request: {type(result).__name__}")
            else:
                # result is guaranteed to be str here (not Exception)
                results.append(str(result))

        # Delay between batches to avoid overwhelming the API
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

    # Generate prompts for all violations
    prompts = []
    for violation in violations:
        # Format prompt using the template
        # Assuming template is a callable that formats the violation
        if callable(analysis_prompt_template):
            prompt = analysis_prompt_template(violation)
        else:
            # If it's a string template, use simple formatting
            prompt = analysis_prompt_template.format(**violation)
        prompts.append(prompt)

    # Process in batches
    responses = await batch_llm_calls(prompts)

    # Combine responses with violations
    analyzed_violations = []
    for violation, response in zip(violations, responses, strict=False):
        analyzed = violation.copy()
        analyzed["llm_analysis"] = response
        analyzed_violations.append(analyzed)

    return analyzed_violations
