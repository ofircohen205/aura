"""
Logging Infrastructure

Structured logging setup with request/response middleware and correlation IDs.
Uses loguru for structured logging with JSON output in production.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to requests for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add correlation ID."""
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        response = await call_next(request)

        response.headers["X-Correlation-ID"] = correlation_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        start_time = time.time()

        logger.info(
            "Request received",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", "")[:100]
                if request.headers.get("user-agent")
                else None,
            },
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                },
            )

            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as exc:
            process_time = time.time() - start_time

            logger.error(
                "Request failed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "process_time": f"{process_time:.3f}s",
                },
                exc_info=True,
            )

            raise
