"""
CSRF Protection Middleware

Provides CSRF (Cross-Site Request Forgery) protection for state-changing operations.
Uses double-submit cookie pattern for stateless CSRF protection.
"""

import secrets
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import get_settings

settings = get_settings()

# CSRF token cookie name
CSRF_TOKEN_COOKIE = "csrf-token"
# CSRF token header name
CSRF_TOKEN_HEADER = "X-CSRF-Token"

# HTTP methods that require CSRF protection (state-changing operations)
PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against CSRF attacks.

    Uses double-submit cookie pattern:
    1. Server sets a CSRF token in a cookie
    2. Client must send the same token in a header for protected requests
    3. Server validates that cookie and header tokens match

    This pattern works well for stateless APIs and doesn't require server-side storage.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate CSRF token for protected methods."""
        # Skip CSRF check for safe methods (GET, HEAD, OPTIONS)
        if request.method not in PROTECTED_METHODS:
            response = await call_next(request)
            # Set CSRF token cookie for all responses (if not already set)
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

        # For protected methods, validate CSRF token
        cookie_token = request.cookies.get(CSRF_TOKEN_COOKIE)
        header_token = request.headers.get(CSRF_TOKEN_HEADER)

        # Both cookie and header must be present
        if not cookie_token or not header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Please include X-CSRF-Token header.",
            )

        # Tokens must match
        if cookie_token != header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch. Token in cookie and header must match.",
            )

        # Process request
        response = await call_next(request)

        # Ensure CSRF token cookie is set in response (refresh if needed)
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
