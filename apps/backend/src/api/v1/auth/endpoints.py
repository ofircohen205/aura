"""Authentication API Endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request, status
from loguru import logger

from api.dependencies import get_current_active_user
from api.exceptions import (
    BaseApplicationException,
    application_exception_handler,
    generic_exception_handler,
)
from api.logging import get_log_context, log_operation
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
from core.metrics import (
    auth_failures_total,
    auth_requests_total,
    auth_token_refreshes_total,
    metrics_helper,
    tokens_issued_total,
    user_registrations_total,
)
from db.database import AsyncSession, SessionDep
from db.models.user import User
from services.auth.service import auth_service

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
    request: Request,
) -> TokenResponse:
    """
    Register a new user.

    Creates a new user account with the provided email, username, and password.
    The password is hashed using bcrypt before storage.
    Returns access and refresh tokens for immediate authentication.
    """
    with log_operation(
        "user_register",
        request,
        email=user_data.email,
        username=user_data.username,
    ) as op_ctx:
        try:
            user = await auth_service.register_user(
                session=session,
                email=user_data.email,
                username=user_data.username,
                password=user_data.password,
            )

            op_ctx["user_id"] = str(user.id)

            access_token = await auth_service.create_access_token(user)
            metrics_helper.inc_counter(tokens_issued_total, token_type="access")

            refresh_token = await auth_service.create_refresh_token_record(user=user)
            metrics_helper.inc_counter(tokens_issued_total, token_type="refresh")

            metrics_helper.inc_counter(user_registrations_total, status="success")
            metrics_helper.inc_counter(auth_requests_total, endpoint="register", status="success")

            logger.info(
                "User registration successful",
                extra=op_ctx,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except Exception as e:
            op_ctx["error"] = str(e)
            op_ctx["error_type"] = type(e).__name__
            metrics_helper.inc_counter(user_registrations_total, status="failure")
            metrics_helper.inc_counter(auth_requests_total, endpoint="register", status="failure")
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
    request: Request,
) -> TokenResponse:
    """
    Authenticate a user and receive tokens.

    Validates user credentials and returns JWT access token and refresh token.
    """
    with log_operation(
        "user_login",
        request,
        email=credentials.email,
    ) as op_ctx:
        try:
            user = await auth_service.authenticate_user(
                session=session,
                email=credentials.email,
                password=credentials.password,
            )

            op_ctx["user_id"] = str(user.id)

            access_token = await auth_service.create_access_token(user)
            metrics_helper.inc_counter(tokens_issued_total, token_type="access")

            refresh_token = await auth_service.create_refresh_token_record(user=user)
            metrics_helper.inc_counter(tokens_issued_total, token_type="refresh")

            metrics_helper.inc_counter(auth_requests_total, endpoint="login", status="success")

            logger.info(
                "User login successful",
                extra=op_ctx,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except Exception as e:
            op_ctx["error"] = str(e)
            op_ctx["error_type"] = type(e).__name__
            metrics_helper.inc_counter(auth_requests_total, endpoint="login", status="failure")
            error_type = type(e).__name__
            if "InvalidCredentialsError" in error_type:
                metrics_helper.inc_counter(auth_failures_total, reason="invalid_credentials")
            elif "InactiveUserError" in error_type:
                metrics_helper.inc_counter(auth_failures_total, reason="inactive_user")
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
    request: Request,
) -> TokenResponse:
    """
    Refresh an access token.

    Validates the refresh token and returns a new access token.
    The refresh token remains valid until it expires.
    """
    with log_operation(
        "token_refresh",
        request,
        token_preview=token_data.refresh_token[:10] + "..."
        if len(token_data.refresh_token) > 10
        else "***",
    ) as op_ctx:
        try:
            access_token, refresh_token = await auth_service.refresh_access_token(
                session=session,
                refresh_token_str=token_data.refresh_token,
            )
            metrics_helper.inc_counter(auth_token_refreshes_total, status="success")
            metrics_helper.inc_counter(tokens_issued_total, token_type="access")
            metrics_helper.inc_counter(auth_requests_total, endpoint="refresh", status="success")

            logger.info(
                "Token refresh successful",
                extra=op_ctx,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except Exception as e:
            op_ctx["error"] = str(e)
            op_ctx["error_type"] = type(e).__name__
            metrics_helper.inc_counter(auth_token_refreshes_total, status="failure")
            metrics_helper.inc_counter(auth_requests_total, endpoint="refresh", status="failure")
            error_type = type(e).__name__
            if "RefreshTokenNotFoundError" in error_type:
                metrics_helper.inc_counter(auth_failures_total, reason="invalid_token")
            elif "TokenExpiredError" in error_type:
                metrics_helper.inc_counter(auth_failures_total, reason="expired_token")
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
    request: Request,
) -> dict[str, str]:
    """
    Log out a user by revoking their refresh token.

    The refresh token is deleted from the database, preventing further use.
    """
    with log_operation(
        "user_logout",
        request,
        token_preview=token_data.refresh_token[:10] + "..."
        if len(token_data.refresh_token) > 10
        else "***",
    ) as op_ctx:
        await auth_service.revoke_refresh_token(
            refresh_token_str=token_data.refresh_token,
        )

        logger.info(
            "User logout successful",
            extra=op_ctx,
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
    request: Request,
) -> UserResponse:
    """
    Get the current user's profile.

    Returns the profile information of the authenticated user.
    """
    log_context = get_log_context(request, user_id=str(current_user.id))
    logger.debug(
        "Getting current user profile",
        extra=log_context,
    )

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
    request: Request,
) -> UserResponse:
    """
    Update the current user's profile.

    Allows updating username and email. Both fields are optional.
    """
    with log_operation(
        "user_profile_update",
        request,
        user_id=str(current_user.id),
        updating_username=user_update.username is not None,
        updating_email=user_update.email is not None,
    ) as op_ctx:
        updated_user = await auth_service.update_user(
            session=session,
            user=current_user,
            username=user_update.username,
            email=user_update.email,
        )

        logger.info(
            "User profile updated successfully",
            extra=op_ctx,
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
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, SessionDep],
    pagination: PaginationParams = Depends(),  # type: ignore[misc]
) -> PaginatedResponse:
    """
    List all users with pagination.

    Requires admin role. Returns paginated list of users.
    """
    from dao.user import user_dao

    log_context = get_log_context(request, user_id=str(current_user.id))

    if "admin" not in current_user.roles:
        from api.exceptions import ForbiddenError

        logger.warning(
            "Non-admin user attempted to list users",
            extra=log_context,
        )
        raise ForbiddenError("Admin role required to list users")

    with log_operation(
        "list_users",
        request,
        user_id=str(current_user.id),
        page=pagination.page,
        page_size=pagination.page_size,
        limit=pagination.limit,
        offset=pagination.offset,
    ) as op_ctx:
        users: list[User] = await user_dao.get_all(
            session=session,
            limit=pagination.limit,
            offset=pagination.offset,
        )

        total = await user_dao.count(session)

        op_ctx["users_returned"] = len(users)
        op_ctx["total_users"] = total

        logger.info(
            "Users listed successfully",
            extra=op_ctx,
        )

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
    request: Request,
) -> BulkOperationResponse:
    """
    Create multiple users in bulk.

    Requires admin role. Returns count of successful and failed creations.
    """
    from api.exceptions import ForbiddenError

    if "admin" not in current_user.roles:
        log_context = get_log_context(request, user_id=str(current_user.id))
        logger.warning(
            "Non-admin user attempted bulk user creation",
            extra=log_context,
        )
        raise ForbiddenError("Admin role required for bulk operations")

    with log_operation(
        "bulk_create_users",
        request,
        user_id=str(current_user.id),
        users_count=len(bulk_data.users),
    ) as op_ctx:
        users_data = [
            {"email": user.email, "username": user.username, "password": user.password}
            for user in bulk_data.users
        ]

        created_users, errors = await auth_service.bulk_create_users(
            session=session,
            users_data=users_data,
        )

        op_ctx["success_count"] = len(created_users)
        op_ctx["error_count"] = len(errors)

        logger.info(
            "Bulk user creation completed",
            extra=op_ctx,
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
    request: Request,
) -> BulkOperationResponse:
    """
    Update multiple users in bulk.

    Requires admin role. Returns count of successful and failed updates.
    """
    from api.exceptions import ForbiddenError

    if "admin" not in current_user.roles:
        log_context = get_log_context(request, user_id=str(current_user.id))
        logger.warning(
            "Non-admin user attempted bulk user update",
            extra=log_context,
        )
        raise ForbiddenError("Admin role required for bulk operations")

    with log_operation(
        "bulk_update_users",
        request,
        user_id=str(current_user.id),
        updates_count=len(bulk_data.user_updates),
    ) as op_ctx:
        updated_users, errors = await auth_service.bulk_update_users(
            session=session,
            updates=bulk_data.user_updates,
        )

        op_ctx["success_count"] = len(updated_users)
        op_ctx["error_count"] = len(errors)

        logger.info(
            "Bulk user update completed",
            extra=op_ctx,
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
    request: Request,
) -> BulkOperationResponse:
    """
    Delete multiple users in bulk.

    Requires admin role. Returns count of successful and failed deletions.
    """
    from api.exceptions import ForbiddenError

    if "admin" not in current_user.roles:
        log_context = get_log_context(request, user_id=str(current_user.id))
        logger.warning(
            "Non-admin user attempted bulk user deletion",
            extra=log_context,
        )
        raise ForbiddenError("Admin role required for bulk operations")

    with log_operation(
        "bulk_delete_users",
        request,
        user_id=str(current_user.id),
        user_ids_count=len(bulk_data.user_ids),
    ) as op_ctx:
        deleted_count, errors = await auth_service.bulk_delete_users(
            session=session,
            user_ids=bulk_data.user_ids,
        )

        op_ctx["success_count"] = deleted_count
        op_ctx["error_count"] = len(errors)

        logger.info(
            "Bulk user deletion completed",
            extra=op_ctx,
        )

        return BulkOperationResponse(
            success_count=deleted_count,
            error_count=len(errors),
            errors=errors,
        )


def create_auth_app() -> FastAPI:
    """Create and configure the authentication service FastAPI sub-application."""
    app = FastAPI(title="Authentication API")
    app.add_exception_handler(BaseApplicationException, application_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    register_exception_handlers(app)
    app.include_router(router)
    return app
