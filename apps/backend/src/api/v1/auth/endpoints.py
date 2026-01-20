"""Authentication API Endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, status

from api.dependencies import get_current_active_user
from api.v1.auth.exceptions import register_exception_handlers
from api.v1.auth.schemas import (
    BulkOperationResponse,
    BulkUserCreate,
    BulkUserDelete,
    BulkUserUpdate,
    PaginatedResponse,
    PaginationParams,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from db.database import AsyncSession, SessionDep
from db.models.user import User
from services.auth.service import auth_service

# Import metrics (optional, fails gracefully if prometheus_client not installed)
try:
    from core.metrics import (
        auth_failures_total,
        auth_requests_total,
        auth_token_refreshes_total,
        tokens_issued_total,
        user_registrations_total,
    )

    METRICS_ENABLED = True
except ImportError:
    # Metrics not available
    METRICS_ENABLED = False
    auth_requests_total = None
    auth_token_refreshes_total = None
    user_registrations_total = None
    auth_failures_total = None
    tokens_issued_total = None

router = APIRouter(tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password. Returns access and refresh tokens.",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        409: {"description": "User already exists"},
        400: {"description": "Validation error"},
    },
)
async def register(
    user_data: UserRegister,
    session: Annotated[AsyncSession, SessionDep],
) -> TokenResponse:
    """
    Register a new user.

    Creates a new user account with the provided email, username, and password.
    The password is hashed using bcrypt before storage.
    Returns access and refresh tokens for immediate authentication.
    """
    try:
        user = await auth_service.register_user(
            session=session,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
        )

        # Create access token
        access_token = await auth_service.create_access_token(user)
        if METRICS_ENABLED:
            tokens_issued_total.labels(token_type="access").inc()

        # Create refresh token
        refresh_token = await auth_service.create_refresh_token_record(user=user)
        if METRICS_ENABLED:
            tokens_issued_total.labels(token_type="refresh").inc()

        if METRICS_ENABLED:
            user_registrations_total.labels(status="success").inc()
            auth_requests_total.labels(endpoint="register", status="success").inc()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except Exception:
        if METRICS_ENABLED:
            user_registrations_total.labels(status="failure").inc()
            auth_requests_total.labels(endpoint="register", status="failure").inc()
        raise


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate a user and receive access and refresh tokens.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Invalid credentials"},
        403: {"description": "User account is inactive"},
    },
)
async def login(
    credentials: UserLogin,
    session: Annotated[AsyncSession, SessionDep],
) -> TokenResponse:
    """
    Authenticate a user and receive tokens.

    Validates user credentials and returns JWT access token and refresh token.
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            session=session,
            email=credentials.email,
            password=credentials.password,
        )

        # Create access token
        access_token = await auth_service.create_access_token(user)
        if METRICS_ENABLED:
            tokens_issued_total.labels(token_type="access").inc()

        # Create refresh token
        refresh_token = await auth_service.create_refresh_token_record(user=user)
        if METRICS_ENABLED:
            tokens_issued_total.labels(token_type="refresh").inc()

        if METRICS_ENABLED:
            auth_requests_total.labels(endpoint="login", status="success").inc()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except Exception as e:
        if METRICS_ENABLED:
            auth_requests_total.labels(endpoint="login", status="failure").inc()
            # Track specific failure reasons
            error_type = type(e).__name__
            if "InvalidCredentialsError" in error_type:
                auth_failures_total.labels(reason="invalid_credentials").inc()
            elif "InactiveUserError" in error_type:
                auth_failures_total.labels(reason="inactive_user").inc()
        raise


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh(
    token_data: RefreshTokenRequest,
    session: Annotated[AsyncSession, SessionDep],
) -> TokenResponse:
    """
    Refresh an access token.

    Validates the refresh token and returns a new access token.
    The refresh token remains valid until it expires.
    """
    try:
        access_token, refresh_token = await auth_service.refresh_access_token(
            session=session,
            refresh_token_str=token_data.refresh_token,
        )
        if METRICS_ENABLED:
            auth_token_refreshes_total.labels(status="success").inc()
            tokens_issued_total.labels(token_type="access").inc()
            auth_requests_total.labels(endpoint="refresh", status="success").inc()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except Exception as e:
        if METRICS_ENABLED:
            auth_token_refreshes_total.labels(status="failure").inc()
            auth_requests_total.labels(endpoint="refresh", status="failure").inc()
            error_type = type(e).__name__
            if "RefreshTokenNotFoundError" in error_type:
                auth_failures_total.labels(reason="invalid_token").inc()
            elif "TokenExpiredError" in error_type:
                auth_failures_total.labels(reason="expired_token").inc()
        raise


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Revoke a refresh token to log out the user.",
    responses={
        200: {"description": "Logout successful"},
    },
)
async def logout(
    token_data: RefreshTokenRequest,
    session: Annotated[AsyncSession, SessionDep],
) -> dict[str, str]:
    """
    Log out a user by revoking their refresh token.

    The refresh token is deleted from the database, preventing further use.
    """
    await auth_service.revoke_refresh_token(
        refresh_token_str=token_data.refresh_token,
    )

    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """
    Get the current user's profile.

    Returns the profile information of the authenticated user.
    """
    user_response = UserResponse.model_validate(current_user)
    user_response.links = {
        "self": "/api/v1/auth/me",
        "update": "/api/v1/auth/me",
    }
    return user_response


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user.",
    responses={
        200: {"description": "User profile updated successfully"},
        401: {"description": "Unauthorized"},
        409: {"description": "Email or username already exists"},
    },
)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
) -> UserResponse:
    """
    Update the current user's profile.

    Allows updating username and email. Both fields are optional.
    """
    updated_user = await auth_service.update_user(
        session=session,
        user=current_user,
        username=user_update.username,
        email=user_update.email,
    )

    user_response = UserResponse.model_validate(updated_user)
    user_response.links = {
        "self": "/api/v1/auth/me",
        "update": "/api/v1/auth/me",
    }
    return user_response


@router.get(
    "/users",
    response_model=PaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List users (admin only)",
    description="Get a paginated list of all users. Requires admin role.",
    responses={
        200: {"description": "Users retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - admin role required"},
    },
)
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
    pagination: PaginationParams = Depends(),  # type: ignore[misc]
) -> PaginatedResponse:
    """
    List all users with pagination.

    Requires admin role. Returns paginated list of users.
    """
    from dao.user import user_dao

    # Check admin role
    if "admin" not in current_user.roles:
        from core.exceptions import ForbiddenError

        raise ForbiddenError("Admin role required to list users")

    # Get users with pagination
    users: list[User] = await user_dao.get_all(
        session=session,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    # Get total count
    total = await user_dao.count(session)

    # Convert to response models
    user_responses = [UserResponse.model_validate(user) for user in users]

    return PaginatedResponse.create(
        items=user_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/users/bulk",
    response_model=BulkOperationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create users (admin only)",
    description="Create multiple users in a single operation. Requires admin role.",
    responses={
        201: {"description": "Bulk creation completed"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - admin role required"},
    },
)
async def bulk_create_users(
    bulk_data: BulkUserCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
) -> BulkOperationResponse:
    """
    Create multiple users in bulk.

    Requires admin role. Returns count of successful and failed creations.
    """
    from core.exceptions import ForbiddenError

    # Check admin role
    if "admin" not in current_user.roles:
        raise ForbiddenError("Admin role required for bulk operations")

    # Convert to service format
    users_data = [
        {"email": user.email, "username": user.username, "password": user.password}
        for user in bulk_data.users
    ]

    created_users, errors = await auth_service.bulk_create_users(
        session=session,
        users_data=users_data,
    )

    return BulkOperationResponse(
        success_count=len(created_users),
        error_count=len(errors),
        errors=errors,
    )


@router.patch(
    "/users/bulk",
    response_model=BulkOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk update users (admin only)",
    description="Update multiple users in a single operation. Requires admin role.",
    responses={
        200: {"description": "Bulk update completed"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - admin role required"},
    },
)
async def bulk_update_users(
    bulk_data: BulkUserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
) -> BulkOperationResponse:
    """
    Update multiple users in bulk.

    Requires admin role. Returns count of successful and failed updates.
    """
    from core.exceptions import ForbiddenError

    # Check admin role
    if "admin" not in current_user.roles:
        raise ForbiddenError("Admin role required for bulk operations")

    updated_users, errors = await auth_service.bulk_update_users(
        session=session,
        updates=bulk_data.user_updates,
    )

    return BulkOperationResponse(
        success_count=len(updated_users),
        error_count=len(errors),
        errors=errors,
    )


@router.delete(
    "/users/bulk",
    response_model=BulkOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk delete users (admin only)",
    description="Delete multiple users in a single operation. Requires admin role.",
    responses={
        200: {"description": "Bulk deletion completed"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - admin role required"},
    },
)
async def bulk_delete_users(
    bulk_data: BulkUserDelete,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
) -> BulkOperationResponse:
    """
    Delete multiple users in bulk.

    Requires admin role. Returns count of successful and failed deletions.
    """
    from core.exceptions import ForbiddenError

    # Check admin role
    if "admin" not in current_user.roles:
        raise ForbiddenError("Admin role required for bulk operations")

    deleted_count, errors = await auth_service.bulk_delete_users(
        session=session,
        user_ids=bulk_data.user_ids,
    )

    return BulkOperationResponse(
        success_count=deleted_count,
        error_count=len(errors),
        errors=errors,
    )


def create_auth_app() -> FastAPI:
    """Create and configure the authentication service FastAPI sub-application."""
    app = FastAPI(title="Authentication API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
