"""Authentication API Endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, status

from api.dependencies import get_current_active_user
from api.v1.auth.exceptions import register_exception_handlers
from api.v1.auth.schemas import (
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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password.",
    responses={
        201: {"description": "User registered successfully"},
        409: {"description": "User already exists"},
        400: {"description": "Validation error"},
    },
)
async def register(
    user_data: UserRegister,
    session: Annotated[AsyncSession, SessionDep],
) -> UserResponse:
    """
    Register a new user.

    Creates a new user account with the provided email, username, and password.
    The password is hashed using bcrypt before storage.
    """
    user = await auth_service.register_user(
        session=session,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate a user and receive access and refresh tokens.",
    responses={
        200: {"description": "Login successful"},
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
    # Authenticate user
    user = await auth_service.authenticate_user(
        session=session,
        email=credentials.email,
        password=credentials.password,
    )

    # Create access token
    access_token = await auth_service.create_access_token(user)

    # Create refresh token
    refresh_token = await auth_service.create_refresh_token_record(user=user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


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
    access_token, refresh_token = await auth_service.refresh_access_token(
        session=session,
        refresh_token_str=token_data.refresh_token,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


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
    return UserResponse.model_validate(current_user)


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

    return UserResponse.model_validate(updated_user)


def create_auth_app() -> FastAPI:
    """Create and configure the authentication service FastAPI sub-application."""
    app = FastAPI(title="Authentication API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
