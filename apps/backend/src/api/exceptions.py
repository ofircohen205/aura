"""
Exception Handling Framework

Base exception classes and HTTP exception mapping utilities.
Provides consistent error handling across the application.
"""

from typing import Any, TypeVar

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

T = TypeVar("T", bound=Response)


def add_cors_headers[T: Response](response: T, request: Request) -> T:
    """
    Add CORS headers to a response based on the request origin.

    This ensures CORS headers are present on error responses that might
    bypass the CORS middleware.

    Args:
        response: The response to add headers to
        request: The request object to check origin from

    Returns:
        Response with CORS headers added
    """
    from core.config import get_settings

    settings = get_settings()
    origin = request.headers.get("origin")

    # Always add CORS headers if origin is present and allowed, or if we're in local dev
    # This ensures error responses are accessible from the frontend
    if origin and (
        "*" in settings.cors_allow_origins
        or origin in settings.cors_allow_origins
        or settings.environment.value == "local"
    ):
        response.headers["Access-Control-Allow-Origin"] = origin
        if settings.cors_allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

    # Add allowed headers and methods for preflight
    if request.method == "OPTIONS":
        if "*" in settings.cors_allow_headers:
            response.headers["Access-Control-Allow-Headers"] = "*"
        else:
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                settings.cors_allow_headers
            )

        if "*" in settings.cors_allow_methods:
            response.headers["Access-Control-Allow-Methods"] = "*"
        else:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                settings.cors_allow_methods
            )

    return response


class BaseApplicationException(Exception):
    """Base exception for all application-specific exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize base application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code for this exception
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BaseApplicationException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(BaseApplicationException):
    """Exception raised when input validation fails."""

    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ConflictError(BaseApplicationException):
    """Exception raised when a resource conflict occurs."""

    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class UnauthorizedError(BaseApplicationException):
    """Exception raised when authentication is required or fails."""

    def __init__(self, message: str = "Unauthorized", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenError(BaseApplicationException):
    """Exception raised when access is forbidden."""

    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ServiceUnavailableError(BaseApplicationException):
    """Exception raised when a service is temporarily unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class InternalServerError(BaseApplicationException):
    """Exception raised for internal server errors."""

    def __init__(
        self, message: str = "Internal server error", details: dict[str, Any] | None = None
    ):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


def create_error_response(
    request: Request,
    exc: BaseApplicationException,
    correlation_id: str | None = None,
) -> JSONResponse:
    """
    Create a standardized error response from an application exception.

    Args:
        request: FastAPI request object
        exc: Application exception instance
        correlation_id: Optional correlation ID for request tracing

    Returns:
        JSONResponse with standardized error format
    """
    error_response = {
        "error": {
            "message": exc.message,
            "type": exc.__class__.__name__,
            "status_code": exc.status_code,
        },
    }

    # Add details if present
    if exc.details:
        error_response["error"]["details"] = exc.details

    # Add correlation ID if available
    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    # Add request path for debugging
    error_response["error"]["path"] = request.url.path

    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )

    # Ensure CORS headers are present on error responses
    return add_cors_headers(response, request)


async def application_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for BaseApplicationException.

    Args:
        request: FastAPI request object
        exc: Application exception instance

    Returns:
        JSONResponse with error details
    """
    # Type narrowing: we know this is BaseApplicationException from the handler registration
    if not isinstance(exc, BaseApplicationException):
        # This shouldn't happen, but handle gracefully
        raise TypeError(f"Expected BaseApplicationException, got {type(exc)}")

    # Type narrowing ensures exc is BaseApplicationException here
    app_exc: BaseApplicationException = exc

    # Try to get correlation ID from request state (set by logging middleware)
    correlation_id = getattr(request.state, "correlation_id", None)

    # Log the application exception (use appropriate log level based on status code)
    log_level = logger.warning if app_exc.status_code < 500 else logger.error
    log_level(
        "Application exception raised",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": app_exc.status_code,
            "error_type": app_exc.__class__.__name__,
            "message": app_exc.message,
            "details": app_exc.details,
        },
    )

    response = create_error_response(request, app_exc, correlation_id)

    # Ensure CORS headers are present on error responses
    return add_cors_headers(response, request)


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Unhandled exception instance

    Returns:
        JSONResponse with error details
    """
    from core.config import get_settings

    settings = get_settings()
    correlation_id = getattr(request.state, "correlation_id", None)

    # Log the exception
    logger.error(
        "Unhandled exception occurred",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
        },
        exc_info=True,
    )

    # Sanitize error messages in production to prevent information disclosure
    if settings.environment.value == "production":
        error_message = "An unexpected error occurred"
        error_type = "InternalServerError"
    else:
        error_message = str(exc)
        error_type = exc.__class__.__name__

    error_response = {
        "error": {
            "message": error_message,
            "type": error_type,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": request.url.path,
        },
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )

    # Ensure CORS headers are present on error responses
    return add_cors_headers(response, request)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """
    Global exception handler for FastAPI HTTPException.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse with error details
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    origin = request.headers.get("origin")

    # Log the HTTP exception (use appropriate log level based on status code)
    log_level = logger.warning if exc.status_code < 500 else logger.error
    log_level(
        "HTTP exception raised",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "origin": origin,
        },
    )

    error_response = {
        "error": {
            "message": exc.detail,
            "type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )

    # Ensure CORS headers are present on error responses
    response = add_cors_headers(response, request)

    # Log CORS headers for debugging
    logger.debug(
        "CORS headers added to error response",
        extra={
            "correlation_id": correlation_id,
            "origin": origin,
            "cors_origin_header": response.headers.get("Access-Control-Allow-Origin"),
            "cors_credentials_header": response.headers.get("Access-Control-Allow-Credentials"),
        },
    )

    return response
