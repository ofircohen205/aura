"""
Authentication API Tests

Comprehensive tests for authentication endpoints and flows.
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402
from core.security import create_jwt_token  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

# Test data
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
TEST_SECRET_KEY = "test-secret-key-for-jwt-tokens-minimum-32-chars"


@pytest.fixture
def mock_jwt_secret_key(monkeypatch):
    """Set JWT secret key for testing."""
    monkeypatch.setenv("JWT_SECRET_KEY", TEST_SECRET_KEY)


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    mock_session = AsyncMock()
    return mock_session


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, mock_jwt_secret_key):
        """Test successful user registration."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            # Mock user creation
            from uuid import uuid4

            from db.models.user import User

            mock_user = User(
                id=uuid4(),
                email=TEST_EMAIL,
                username=TEST_USERNAME,
                hashed_password="hashed_password",
                is_active=True,
                is_verified=False,
                roles=["user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            with patch("services.auth.service.auth_service.register_user") as mock_register:
                mock_register.return_value = mock_user

                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": TEST_EMAIL,
                        "username": TEST_USERNAME,
                        "password": TEST_PASSWORD,
                    },
                )

                assert response.status_code == 201
                data = response.json()
                assert data["email"] == TEST_EMAIL
                assert data["username"] == TEST_USERNAME
                assert "hashed_password" not in data
                assert data["is_active"] is True

    def test_register_duplicate_email(self, mock_jwt_secret_key):
        """Test registration with duplicate email."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            from services.auth.exceptions import UserAlreadyExistsError

            with patch("services.auth.service.auth_service.register_user") as mock_register:
                mock_register.side_effect = UserAlreadyExistsError(email=TEST_EMAIL)

                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": TEST_EMAIL,
                        "username": TEST_USERNAME,
                        "password": TEST_PASSWORD,
                    },
                )

                assert response.status_code == 409

    def test_register_weak_password(self, mock_jwt_secret_key):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": TEST_EMAIL,
                "username": TEST_USERNAME,
                "password": "short",  # Too short
            },
        )

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, mock_jwt_secret_key):
        """Test successful user login."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            from uuid import uuid4

            from db.models.user import User

            mock_user = User(
                id=uuid4(),
                email=TEST_EMAIL,
                username=TEST_USERNAME,
                hashed_password="hashed_password",
                is_active=True,
                is_verified=False,
                roles=["user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            with (
                patch("services.auth.service.auth_service.authenticate_user") as mock_auth,
                patch("services.auth.service.auth_service.create_access_token") as mock_access,
                patch(
                    "services.auth.service.auth_service.create_refresh_token_record"
                ) as mock_refresh,
            ):
                mock_auth.return_value = mock_user
                mock_access.return_value = "access_token_string"
                mock_refresh.return_value = "refresh_token_string"

                response = client.post(
                    "/api/v1/auth/login",
                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, mock_jwt_secret_key):
        """Test login with invalid credentials."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            from services.auth.exceptions import InvalidCredentialsError

            with patch("services.auth.service.auth_service.authenticate_user") as mock_auth:
                mock_auth.side_effect = InvalidCredentialsError()

                response = client.post(
                    "/api/v1/auth/login",
                    json={"email": TEST_EMAIL, "password": "wrong_password"},
                )

                assert response.status_code == 401

    def test_login_inactive_user(self, mock_jwt_secret_key):
        """Test login with inactive user account."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            from services.auth.exceptions import InactiveUserError

            with patch("services.auth.service.auth_service.authenticate_user") as mock_auth:
                mock_auth.side_effect = InactiveUserError()

                response = client.post(
                    "/api/v1/auth/login",
                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                )

                assert response.status_code == 403


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_refresh_success(self, mock_jwt_secret_key):
        """Test successful token refresh."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("services.auth.service.auth_service.refresh_access_token") as mock_refresh:
                mock_refresh.return_value = ("new_access_token", "valid_refresh_token")

                response = client.post(
                    "/api/v1/auth/refresh",
                    json={"refresh_token": "valid_refresh_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["access_token"] == "new_access_token"
                assert "refresh_token" in data

    def test_refresh_invalid_token(self, mock_jwt_secret_key):
        """Test refresh with invalid token."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            from services.auth.exceptions import RefreshTokenNotFoundError

            with patch("services.auth.service.auth_service.refresh_access_token") as mock_refresh:
                mock_refresh.side_effect = RefreshTokenNotFoundError()

                response = client.post(
                    "/api/v1/auth/refresh",
                    json={"refresh_token": "invalid_token"},
                )

                assert response.status_code == 401


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_success(self, mock_jwt_secret_key):
        """Test successful logout."""
        with patch("api.v1.auth.endpoints.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("services.auth.service.auth_service.revoke_refresh_token") as mock_revoke:
                mock_revoke.return_value = None

                response = client.post(
                    "/api/v1/auth/logout",
                    json={"refresh_token": "refresh_token_to_revoke"},
                )

                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                assert "successfully" in data["message"].lower()


class TestUserProfile:
    """Tests for user profile endpoints."""

    def test_get_current_user_profile(self, mock_jwt_secret_key):
        """Test getting current user profile."""
        from uuid import uuid4

        from db.models.user import User

        mock_user = User(
            id=uuid4(),
            email=TEST_EMAIL,
            username=TEST_USERNAME,
            hashed_password="hashed_password",
            is_active=True,
            is_verified=False,
            roles=["user"],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Create a valid JWT token
        token = create_jwt_token(
            payload={"sub": str(mock_user.id), "email": TEST_EMAIL},
            secret_key=TEST_SECRET_KEY,
            expires_delta=timedelta(minutes=30),
        )

        with patch("core.dependencies.get_current_user") as mock_get_user:
            mock_get_user.return_value = mock_user

            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == TEST_EMAIL
            assert data["username"] == TEST_USERNAME
            assert "hashed_password" not in data

    def test_get_profile_unauthorized(self, mock_jwt_secret_key):
        """Test getting profile without authentication."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 422  # Missing authorization header

    def test_update_user_profile(self, mock_jwt_secret_key):
        """Test updating user profile."""
        from uuid import uuid4

        from db.models.user import User

        mock_user = User(
            id=uuid4(),
            email=TEST_EMAIL,
            username=TEST_USERNAME,
            hashed_password="hashed_password",
            is_active=True,
            is_verified=False,
            roles=["user"],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        updated_user = User(
            id=mock_user.id,
            email="newemail@example.com",
            username="newusername",
            hashed_password=mock_user.hashed_password,
            is_active=mock_user.is_active,
            is_verified=mock_user.is_verified,
            roles=mock_user.roles,
            created_at=mock_user.created_at,
            updated_at=datetime.now(UTC),
        )

        token = create_jwt_token(
            payload={"sub": str(mock_user.id), "email": TEST_EMAIL},
            secret_key=TEST_SECRET_KEY,
            expires_delta=timedelta(minutes=30),
        )

        with (
            patch("core.dependencies.get_current_user") as mock_get_user,
            patch("api.v1.auth.endpoints.get_session") as mock_get_session,
        ):
            mock_get_user.return_value = mock_user
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("services.auth.service.auth_service.update_user") as mock_update:
                mock_update.return_value = updated_user

                response = client.patch(
                    "/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"email": "newemail@example.com", "username": "newusername"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "newemail@example.com"
                assert data["username"] == "newusername"


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        from core.security import hash_password, verify_password

        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_wrong_password(self):
        """Test password verification with wrong password."""
        from core.security import hash_password, verify_password

        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_jwt_token(self, mock_jwt_secret_key):
        """Test JWT token creation."""
        from core.security import create_jwt_token

        payload = {"sub": "user123", "email": "test@example.com"}
        token = create_jwt_token(
            payload=payload,
            secret_key=TEST_SECRET_KEY,
            expires_delta=timedelta(minutes=30),
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_jwt_token(self, mock_jwt_secret_key):
        """Test JWT token verification."""
        from core.security import create_jwt_token, verify_jwt_token

        payload = {"sub": "user123", "email": "test@example.com"}
        token = create_jwt_token(
            payload=payload,
            secret_key=TEST_SECRET_KEY,
            expires_delta=timedelta(minutes=30),
        )

        decoded = verify_jwt_token(token, TEST_SECRET_KEY)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"

    def test_verify_jwt_token_invalid(self, mock_jwt_secret_key):
        """Test JWT token verification with invalid token."""
        from core.security import verify_jwt_token

        decoded = verify_jwt_token("invalid_token", TEST_SECRET_KEY)
        assert decoded is None

    def test_verify_jwt_token_wrong_secret(self, mock_jwt_secret_key):
        """Test JWT token verification with wrong secret key."""
        from core.security import create_jwt_token, verify_jwt_token

        payload = {"sub": "user123"}
        token = create_jwt_token(
            payload=payload,
            secret_key=TEST_SECRET_KEY,
            expires_delta=timedelta(minutes=30),
        )

        decoded = verify_jwt_token(token, "wrong_secret_key")
        assert decoded is None
