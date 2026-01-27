"""
Logging Infrastructure

Structured logging setup with request/response middleware and correlation IDs.
Uses loguru for structured logging with JSON output in production.
"""

import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from api.logging import sanitize_for_logging

_REDACTED = "***REDACTED***"
_SENSITIVE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "code",
    "key",
    "password",
    "refresh_token",
    "secret",
    "session",
    "token",
}


def _get_auth_scheme(request: Request) -> str | None:
    """Return Authorization scheme (e.g. 'bearer') without credentials."""
    auth = request.headers.get("authorization")
    if not auth:
        return None
    parts = auth.split()
    if not parts:
        return None
    return parts[0].lower()


def _sanitize_query_params(request: Request) -> dict[str, Any] | None:
    """Convert query params to a log-safe dict (redact sensitive keys)."""
    if not request.query_params:
        return None

    # Preserve multi-values while keeping output readable.
    acc: dict[str, list[str]] = {}
    for key, value in request.query_params.multi_items():
        key_lower = key.lower()
        safe_value = (
            _REDACTED if key_lower in _SENSITIVE_QUERY_KEYS else str(sanitize_for_logging(value))
        )
        acc.setdefault(key, []).append(safe_value)

    # Collapse singletons to a string for nicer logs.
    collapsed: dict[str, Any] = {}
    for key, values in acc.items():
        collapsed[key] = values[0] if len(values) == 1 else values
    return collapsed


def _parse_forwarded_for(header_value: str) -> list[str]:
    """
    Parse RFC 7239 Forwarded header into a list of 'for' values (best-effort).
    """
    results: list[str] = []
    for part in header_value.split(","):
        params = [p.strip() for p in part.split(";") if p.strip()]
        for param in params:
            if not param.lower().startswith("for="):
                continue
            value = param[4:].strip().strip('"')
            # Common forms: 1.2.3.4, "[2001:db8::1]", "1.2.3.4:1234"
            if value.startswith("[") and "]" in value:
                value = value[1 : value.index("]")]
            if ":" in value and value.count(":") == 1:
                # Likely IPv4:port; keep only host.
                value = value.split(":", 1)[0]
            if value:
                results.append(value)
    return results


def _get_ip_chain(request: Request) -> list[str]:
    """Best-effort chain of client IPs from forwarding headers."""
    forwarded = request.headers.get("forwarded")
    if forwarded:
        forwarded_list = _parse_forwarded_for(forwarded)
        if forwarded_list:
            return forwarded_list

    xff = request.headers.get("x-forwarded-for")
    if xff:
        return [ip.strip() for ip in xff.split(",") if ip.strip()]

    return []


def _get_client_ip(request: Request) -> str | None:
    """Best-effort client IP resolution for observability (not security decisions)."""
    for header in ("cf-connecting-ip", "x-real-ip"):
        value = request.headers.get(header)
        if value:
            return value.strip()

    chain = _get_ip_chain(request)
    if chain:
        return chain[0]

    return request.client.host if request.client else None


def _build_request_context(request: Request, correlation_id: str) -> dict[str, Any]:
    client_ip = _get_client_ip(request)
    ip_chain = _get_ip_chain(request)
    auth_scheme = _get_auth_scheme(request)

    return {
        "correlation_id": correlation_id,
        "method": request.method,
        "path": request.url.path,
        "path_params": request.path_params or None,
        "query_params": _sanitize_query_params(request),
        "client_ip": client_ip,
        "client_ip_chain": ip_chain or None,
        "client_host": request.client.host if request.client else None,
        "client_port": request.client.port if request.client else None,
        "host": request.headers.get("host"),
        "origin": request.headers.get("origin"),
        "referer": request.headers.get("referer"),
        "user_agent": request.headers.get("user-agent", "")[:200]
        if request.headers.get("user-agent")
        else None,
        "auth_scheme": auth_scheme,
        "has_authorization": auth_scheme is not None,
        "request_id": request.headers.get("x-request-id"),
        "aura_client": request.headers.get("x-aura-client"),
        "aura_client_version": request.headers.get("x-aura-client-version"),
        "content_type": request.headers.get("content-type"),
        "content_length": request.headers.get("content-length"),
        "x_forwarded_proto": request.headers.get("x-forwarded-proto"),
        "x_forwarded_host": request.headers.get("x-forwarded-host"),
        "x_forwarded_port": request.headers.get("x-forwarded-port"),
    }


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to requests for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add correlation ID."""
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

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
        request_ctx = _build_request_context(request, correlation_id)
        aura_client = request_ctx.get("aura_client") or "unknown"

        # Put key fields in the message so they're visible in text logs.
        logger.info(
            f"{request.method} {request.url.path} request received "
            f"(cid={correlation_id}, ip={request_ctx.get('client_ip')}, client={aura_client})",
            extra=request_ctx,
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            duration_ms = process_time * 1000

            logger.info(
                f"{request.method} {request.url.path} completed "
                f"(status={response.status_code}, duration_ms={duration_ms:.1f}, "
                f"cid={correlation_id}, ip={request_ctx.get('client_ip')}, client={aura_client})",
                extra={
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "process_time_ms": duration_ms,
                    "response_content_type": response.headers.get("content-type"),
                    "response_content_length": response.headers.get("content-length"),
                    **request_ctx,
                },
            )

            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as exc:
            process_time = time.time() - start_time
            duration_ms = process_time * 1000

            logger.error(
                f"{request.method} {request.url.path} failed "
                f"(error_type={type(exc).__name__}, duration_ms={duration_ms:.1f}, "
                f"cid={correlation_id}, ip={request_ctx.get('client_ip')}, client={aura_client})",
                extra={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "process_time": f"{process_time:.3f}s",
                    "process_time_ms": duration_ms,
                    **request_ctx,
                },
                exc_info=True,
            )

            raise
