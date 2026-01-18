"""
Authentication Service Exceptions

Service-specific exceptions for authentication operations.
"""

from core.exceptions import ConflictError, ForbiddenError, UnauthorizedError, ValidationError


class InvalidCredentialsError(UnauthorizedError):
    """Exception raised when user credentials are invalid."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message=message, details={"error": "invalid_credentials"})


class UserAlreadyExistsError(ConflictError):
    """Exception raised when attempting to register a user that already exists."""

    def __init__(self, email: str | None = None, username: str | None = None):
        details: dict[str, str] = {}
        if email:
            details["email"] = email
        if username:
            details["username"] = username

        message = "User already exists"
        if email:
            message = f"User with email '{email}' already exists"
        elif username:
            message = f"User with username '{username}' already exists"

        super().__init__(message=message, details=details)


class TokenExpiredError(UnauthorizedError):
    """Exception raised when a JWT token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message, details={"error": "token_expired"})


class InvalidTokenError(UnauthorizedError):
    """Exception raised when a JWT token is invalid or malformed."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message, details={"error": "invalid_token"})


class InactiveUserError(ForbiddenError):
    """Exception raised when attempting to authenticate with an inactive user account."""

    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message=message, details={"error": "inactive_user"})


class RefreshTokenNotFoundError(UnauthorizedError):
    """Exception raised when a refresh token is not found or has been revoked."""

    def __init__(self, message: str = "Refresh token not found or expired"):
        super().__init__(message=message, details={"error": "refresh_token_not_found"})


class PasswordValidationError(ValidationError):
    """Exception raised when password validation fails."""

    def __init__(self, message: str, details: dict[str, str] | None = None):
        super().__init__(message=message, details=details or {})
