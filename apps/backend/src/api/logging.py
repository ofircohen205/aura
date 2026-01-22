"""
Logging Helper Utilities

Provides utilities for consistent logging across the application,
including correlation ID extraction and operation timing.
"""

import time
from contextlib import contextmanager
from typing import Any

from fastapi import Request
from loguru import logger


def get_log_context(
    request: Request | None = None,
    **additional_fields: Any,
) -> dict[str, Any]:
    """
    Build a log context dictionary with correlation ID and additional fields.

    Args:
        request: FastAPI request object (optional)
        **additional_fields: Additional fields to include in log context

    Returns:
        Dictionary with correlation_id and additional fields
    """
    context: dict[str, Any] = {}

    def _get_correlation_id() -> str | None:
        if request is None:
            return None
        return getattr(request.state, "correlation_id", None)

    correlation_id = _get_correlation_id()
    if correlation_id:
        context["correlation_id"] = correlation_id
    context.update(additional_fields)
    return context


@contextmanager
def log_operation(
    operation_name: str,
    request: Request | None = None,
    **log_fields: Any,
):
    """
    Context manager for logging operation start, completion, and timing.

    Args:
        operation_name: Name of the operation being logged
        request: FastAPI request object (optional, for correlation ID)
        **log_fields: Additional fields to include in logs

    Yields:
        Dictionary with start_time and operation context

    Example:
        ```python
        with log_operation("rag_query", request, query_length=100) as op_ctx:
            # Perform operation
            result = await service.query(...)
            op_ctx["result_count"] = len(result)
        ```
    """
    start_time = time.time()
    context = get_log_context(request, **log_fields)
    context["operation"] = operation_name

    logger.info(
        f"{operation_name} started",
        extra=context,
    )

    try:
        op_context = {
            "start_time": start_time,
            "operation": operation_name,
            **context,
        }
        yield op_context

        duration = time.time() - start_time
        op_context["duration"] = f"{duration:.3f}s"
        op_context["duration_ms"] = duration * 1000

        logger.info(
            f"{operation_name} completed",
            extra=op_context,
        )
    except Exception as exc:
        duration = time.time() - start_time
        error_context = {
            **context,
            "operation": operation_name,
            "duration": f"{duration:.3f}s",
            "duration_ms": duration * 1000,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }
        logger.error(
            f"{operation_name} failed",
            extra=error_context,
            exc_info=True,
        )
        raise


def sanitize_for_logging(data: Any, max_length: int = 200) -> Any:
    """
    Sanitize data for safe logging (truncate long strings, mask sensitive fields).

    Args:
        data: Data to sanitize
        max_length: Maximum length for string values

    Returns:
        Sanitized data safe for logging
    """
    if isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + "..."
        return data
    elif isinstance(data, dict):
        sanitized = {}
        sensitive_keys = {"password", "token", "secret", "key", "authorization", "auth"}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_for_logging(value, max_length)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item, max_length) for item in data[:10]]  # Limit list size
    else:
        return data
