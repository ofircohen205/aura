"""
CSRF Protection Middleware

Provides CSRF (Cross-Site Request Forgery) protection for state-changing operations.
Uses double-submit cookie pattern for stateless CSRF protection.
"""

import secrets
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import get_settings

settings = get_settings()


CSRF_TOKEN_COOKIE = "csrf-token"
CSRF_TOKEN_HEADER = "X-CSRF-Token"

PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

CSRF_EXEMPT_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
}


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against CSRF attacks.

    Uses double-submit cookie pattern:
    1. Server sets a CSRF token in a cookie
    2. Client must send the same token in a header for protected requests
    3. Server validates that cookie and header tokens match

    This pattern works well for stateless APIs and doesn't require server-side storage.

    Authentication endpoints (login, register, refresh) are exempt from CSRF protection
    because they're called before the user has a session and the CSRF cookie might not
    be set yet. This is a common and secure pattern.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate CSRF token for protected methods."""
        if request.method not in PROTECTED_METHODS:
            response = await call_next(request)
            if CSRF_TOKEN_COOKIE not in request.cookies:
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    CSRF_TOKEN_COOKIE,
                    csrf_token,
                    httponly=False,  # Must be accessible to JavaScript
                    samesite="strict",  # Prevent CSRF attacks
                    secure=settings.environment.value == "production",  # HTTPS only in production
                    max_age=3600 * 24,  # 24 hours
                )
            return response

        if request.url.path in CSRF_EXEMPT_PATHS:
            response = await call_next(request)
            if CSRF_TOKEN_COOKIE not in request.cookies:
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    CSRF_TOKEN_COOKIE,
                    csrf_token,
                    httponly=False,
                    samesite="strict",
                    secure=settings.environment.value == "production",
                    max_age=3600 * 24,
                )
            return response

        cookie_token = request.cookies.get(CSRF_TOKEN_COOKIE)
        header_token = request.headers.get(CSRF_TOKEN_HEADER)

        if not cookie_token or not header_token:
            correlation_id = getattr(request.state, "correlation_id", None)
            logger.warning(
                "CSRF token validation failed - token missing",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "has_cookie_token": bool(cookie_token),
                    "has_header_token": bool(header_token),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Please include X-CSRF-Token header.",
            )

        if cookie_token != header_token:
            correlation_id = getattr(request.state, "correlation_id", None)
            logger.warning(
                "CSRF token validation failed - token mismatch",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch. Token in cookie and header must match.",
            )

        response = await call_next(request)

        if CSRF_TOKEN_COOKIE not in request.cookies:
            csrf_token = secrets.token_urlsafe(32)
            response.set_cookie(
                CSRF_TOKEN_COOKIE,
                csrf_token,
                httponly=False,
                samesite="strict",
                secure=settings.environment.value == "production",
                max_age=3600 * 24,
            )

        return response
