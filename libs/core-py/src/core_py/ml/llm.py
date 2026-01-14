"""
LLM Client Utilities

Provides shared LLM client with retry logic, error handling, rate limiting, and caching.
"""

import logging
import os
from typing import Any

from core_py.ml.config import LLM_ENABLED, LLM_MODEL, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("LLM_RETRY_BACKOFF_FACTOR", "2.0"))
INITIAL_RETRY_DELAY = float(os.getenv("LLM_INITIAL_RETRY_DELAY", "1.0"))


async def get_llm_client():
    """
    Get configured LLM client with proper error handling.

    Returns:
        ChatOpenAI instance if LLM is enabled, None otherwise

    Raises:
        ImportError: If langchain_openai is not installed
        ValueError: If LLM configuration is invalid
    """
    if not LLM_ENABLED:
        logger.debug("LLM is disabled")
        return None

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            max_retries=MAX_RETRIES,
        )

        logger.debug(f"LLM client initialized: model={LLM_MODEL}, temperature={LLM_TEMPERATURE}")
        return llm

    except ImportError as e:
        logger.error(f"langchain_openai not available: {e}")
        raise ImportError(
            "langchain-openai package is required for LLM functionality. "
            "Install it with: pip install langchain-openai"
        ) from e
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}", exc_info=True)
        raise ValueError(f"Invalid LLM configuration: {e}") from e


async def invoke_llm_with_retry(
    prompt: str,
    llm_client: Any | None = None,
    max_retries: int | None = None,
) -> str:
    """
    Invoke LLM with retry logic and comprehensive error handling.

    Args:
        prompt: The prompt to send to the LLM
        llm_client: Optional LLM client instance (will be created if not provided)
        max_retries: Maximum number of retries (defaults to MAX_RETRIES config)

    Returns:
        LLM response content as string

    Raises:
        RuntimeError: If LLM is disabled or all retries failed
        ValueError: If prompt is empty or invalid
    """
    if not LLM_ENABLED:
        raise RuntimeError("LLM is disabled. Set LLM_ENABLED=true to enable.")

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    max_retries = max_retries or MAX_RETRIES

    # Check cache first (async)
    from core_py.ml.cache import get_cached_response as get_cached_response_async

    cached_response = await get_cached_response_async(prompt, LLM_MODEL, LLM_TEMPERATURE)
    if cached_response is not None:
        logger.debug("Returning cached LLM response")
        return cached_response

    llm = llm_client or await get_llm_client()

    if llm is None:
        raise RuntimeError("LLM client could not be initialized")

    import asyncio

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"LLM invocation attempt {attempt + 1}/{max_retries + 1}")
            response = await llm.ainvoke(prompt)

            # Extract content from response
            if hasattr(response, "content"):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            logger.info(
                "LLM invocation successful",
                extra={
                    "attempt": attempt + 1,
                    "model": LLM_MODEL,
                    "response_length": len(content),
                },
            )

            # Cache the response (async)
            from core_py.ml.cache import set_cached_response as set_cached_response_async

            await set_cached_response_async(prompt, content, LLM_MODEL, LLM_TEMPERATURE)

            return content

        except Exception as e:
            last_exception = e
            error_type = type(e).__name__

            # Check for specific OpenAI API errors
            error_message = str(e).lower()

            # Rate limit errors - should retry with backoff
            if ("rate limit" in error_message or "429" in error_message) and attempt < max_retries:
                delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR**attempt)
                logger.warning(
                    f"Rate limit hit, retrying after {delay}s",
                    extra={"attempt": attempt + 1, "error": error_type},
                )
                await asyncio.sleep(delay)
                continue

            # Quota exceeded - don't retry
            if "quota" in error_message or "insufficient_quota" in error_message:
                logger.error(
                    "LLM quota exceeded, cannot retry",
                    extra={"error": error_type, "error_message": str(e)},
                )
                raise RuntimeError(
                    "LLM quota exceeded. Please check your API key and billing status."
                ) from e

            # Authentication errors - don't retry
            if (
                "auth" in error_message
                or "authentication" in error_message
                or "401" in error_message
                or "403" in error_message
            ):
                logger.error(
                    "LLM authentication failed, cannot retry",
                    extra={"error": error_type, "error_message": str(e)},
                )
                raise RuntimeError("LLM authentication failed. Please check your API key.") from e

            # Other errors - retry with backoff
            if attempt < max_retries:
                delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR**attempt)
                logger.warning(
                    f"LLM invocation failed, retrying after {delay}s",
                    extra={
                        "attempt": attempt + 1,
                        "error": error_type,
                        "error_message": str(e)[:200],  # Truncate long error messages
                    },
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "LLM invocation failed after all retries",
                    extra={
                        "max_retries": max_retries,
                        "error": error_type,
                        "error_message": str(e)[:200],
                    },
                    exc_info=True,
                )

    # All retries exhausted
    raise RuntimeError(
        f"LLM invocation failed after {max_retries + 1} attempts. "
        f"Last error: {type(last_exception).__name__}: {str(last_exception)[:200]}"
    ) from last_exception
