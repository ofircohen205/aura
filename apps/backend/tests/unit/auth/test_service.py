"""
Unit Tests for Authentication Service

Tests the business logic of the authentication service in isolation.
Uses mocks for database and Redis dependencies.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from db.models.user import User
from services.auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    RefreshTokenNotFoundError,
    UserAlreadyExistsError,
)
from services.auth.service import AuthService


@pytest.fixture
def auth_service() -> AuthService:
    """Create AuthService instance for testing."""
    return AuthService()


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=False,
        roles=["user"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestAuthServiceRegister:
    """Unit tests for user registration."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, auth_service: AuthService, mock_db_session: AsyncMock, sample_user: User
    ):
        """Test successful user registration."""
        from dao.user import user_dao

        with (
            patch.object(user_dao, "exists_by_email", return_value=False),
            patch.object(user_dao, "exists_by_username", return_value=False),
            patch.object(user_dao, "create", return_value=sample_user),
            patch("services.auth.service.hash_password", return_value="hashed_password"),
        ):
            user = await auth_service.register_user(
                session=mock_db_session,
                email="test@example.com",
                username="testuser",
                password="password123",
            )

            assert user.email == "test@example.com"
            assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self, auth_service: AuthService, mock_db_session: AsyncMock
    ):
        """Test registration with duplicate email."""
        from dao.user import user_dao

        with (
            patch.object(user_dao, "exists_by_email", return_value=True),
            pytest.raises(UserAlreadyExistsError),
        ):
            await auth_service.register_user(
                session=mock_db_session,
                email="existing@example.com",
                username="newuser",
                password="password123",
            )


class TestAuthServiceAuthenticate:
    """Unit tests for user authentication."""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, auth_service: AuthService, mock_db_session: AsyncMock, sample_user: User
    ):
        """Test successful user authentication."""
        from dao.user import user_dao

        with (
            patch.object(user_dao, "get_by_email", return_value=sample_user),
            patch("services.auth.service.verify_password", return_value=True),
        ):
            user = await auth_service.authenticate_user(
                session=mock_db_session,
                email="test@example.com",
                password="password123",
            )

            assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(
        self, auth_service: AuthService, mock_db_session: AsyncMock
    ):
        """Test authentication with invalid credentials."""
        from dao.user import user_dao

        with (
            patch.object(user_dao, "get_by_email", return_value=None),
            pytest.raises(InvalidCredentialsError),
        ):
            await auth_service.authenticate_user(
                session=mock_db_session,
                email="nonexistent@example.com",
                password="password123",
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(
        self, auth_service: AuthService, mock_db_session: AsyncMock, sample_user: User
    ):
        """Test authentication with inactive user."""
        from dao.user import user_dao

        sample_user.is_active = False

        with (
            patch.object(user_dao, "get_by_email", return_value=sample_user),
            patch("services.auth.service.verify_password", return_value=True),
            pytest.raises(InactiveUserError),
        ):
            await auth_service.authenticate_user(
                session=mock_db_session,
                email="test@example.com",
                password="password123",
            )


class TestAuthServiceTokenRefresh:
    """Unit tests for token refresh."""

    @pytest.mark.asyncio
    async def test_refresh_token_not_found(
        self, auth_service: AuthService, mock_db_session: AsyncMock, mock_redis_client: MagicMock
    ):
        """Test token refresh with non-existent token."""
        with patch("services.auth.service.get_redis_client", return_value=mock_redis_client):
            mock_redis_client.get = AsyncMock(return_value=None)

            with pytest.raises(RefreshTokenNotFoundError):
                await auth_service.refresh_access_token(
                    session=mock_db_session,
                    refresh_token_str="invalid_token",
                )
