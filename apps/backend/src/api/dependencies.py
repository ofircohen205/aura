"""
FastAPI Dependencies

Authentication and authorization dependencies for FastAPI endpoints.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from core.config import get_settings
from core.exceptions import ForbiddenError, UnauthorizedError
from core.security import verify_jwt_token
from dao.user import user_dao
from db.database import AsyncSession, SessionDep
from db.models.user import User
from services.auth.service import auth_service

settings = get_settings()


async def get_authorization_header(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """
    Extract and validate authorization header before creating database session.

    This sub-dependency checks authorization first to avoid creating
    a database session when authorization is missing.

    Uses HTTPException to ensure it's handled before any response processing
    starts, preventing "response already started" errors.

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        Authorization header value

    Raises:
        HTTPException: If authorization header is missing (raises immediately before session creation)
    """
    if not authorization:
        # Use HTTPException directly to ensure it's handled before any middleware
        # sends headers, preventing "response already started" errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization


async def get_current_user(
    authorization: Annotated[str, Depends(get_authorization_header)],
    session: Annotated[AsyncSession, SessionDep],
) -> User:
    """
    FastAPI dependency to extract and validate the current user from JWT token.

    Args:
        authorization: Authorization header (Bearer token) - validated by sub-dependency
        session: Database session

    Returns:
        Current User object

    Raises:
        UnauthorizedError: If token is missing, invalid, or expired
    """

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedError("Invalid authentication scheme")
    except ValueError as e:
        raise UnauthorizedError("Invalid authorization header format") from e

    # Verify token
    if not settings.jwt_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret key not configured",
        )

    payload = verify_jwt_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
    if not payload:
        raise UnauthorizedError("Invalid or expired token")

    # Extract user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Token missing user ID")

    # Get user from database
    from uuid import UUID

    try:
        user_id = UUID(user_id_str)
    except ValueError as e:
        raise UnauthorizedError("Invalid user ID in token") from e

    user: User | None = await user_dao.get_by_id(session, user_id)
    if not user:
        raise UnauthorizedError("User not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    FastAPI dependency to ensure the current user is active.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Active User object

    Raises:
        ForbiddenError: If user account is inactive
    """
    if not current_user.is_active:
        raise ForbiddenError("User account is inactive")

    return current_user


def require_role(required_role: str) -> Callable:
    """
    Dependency factory for role-based access control.

    Args:
        required_role: Required role name

    Returns:
        FastAPI dependency function

    Example:
        ```python
        @router.get("/admin")
        async def admin_endpoint(
            user: User = Depends(require_role("admin"))
        ):
            ...
        ```
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """
        Check if user has required role.

        Args:
            current_user: Current active user

        Returns:
            User object if authorized

        Raises:
            ForbiddenError: If user doesn't have required role
        """
        if required_role not in current_user.roles:
            raise ForbiddenError(f"User does not have required role: {required_role}")

        return current_user

    return role_checker


def require_permission(required_permission: str) -> Callable:
    """
    Dependency factory for permission-based access control.

    Args:
        required_permission: Required permission name

    Returns:
        FastAPI dependency function

    Example:
        ```python
        @router.get("/resource")
        async def protected_endpoint(
            user: User = Depends(require_permission("read:resource"))
        ):
            ...
        ```
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """
        Check if user has required permission.

        Args:
            current_user: Current active user

        Returns:
            User object if authorized

        Raises:
            ForbiddenError: If user doesn't have required permission
        """
        has_permission = auth_service.check_permission(current_user, required_permission)
        if not has_permission:
            raise ForbiddenError(f"User does not have required permission: {required_permission}")

        return current_user

    return permission_checker
