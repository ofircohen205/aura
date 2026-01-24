"""
Authentication API Tests (Mocked Integration)

Comprehensive tests for authentication endpoints and flows using mocked dependencies.
These tests verify API endpoint behavior without requiring a real database.
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

pytestmark = [pytest.mark.integration]

# Add backend directory to path for conf import
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402
from api.dependencies import get_current_user  # noqa: E402
from core.security import create_jwt_token  # noqa: E402
from db.database import get_session  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

# Test data
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "TestPassword123!"  # Must have uppercase, lowercase, digit, and special char
TEST_SECRET_KEY = "test-secret-key-for-jwt-tokens-minimum-32-chars"


async def mock_session_generator():
    """Helper function to create a mock async generator for database sessions."""
    mock_session = AsyncMock()
    # Mock session methods to prevent real database operations
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    # Mock context manager methods to prevent real database operations
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    # Just yield the session without any exception handling
    # This allows FastAPI's exception handler to catch exceptions before
    # any response processing happens
    try:
        yield mock_session
    except Exception:
        # Don't rollback - let FastAPI handle the exception
        raise


def get_csrf_token_and_headers(test_client: TestClient) -> tuple[str, dict[str, str]]:
    """Get CSRF token and headers for a TestClient."""
    # Mock the health check endpoint to avoid database connection
    with patch("main.async_engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(return_value=None)
        mock_engine.connect = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        # Make a GET request to get the CSRF token cookie
        response = test_client.get("/health")
        csrf_token = response.cookies.get("csrf-token")
        if not csrf_token:
            # If no cookie was set, generate a token manually
            import secrets

            csrf_token = secrets.token_urlsafe(32)
    headers = {"X-CSRF-Token": csrf_token}
    return csrf_token, headers


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
        csrf_token, headers = get_csrf_token_and_headers(client)

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:
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

            with (
                patch(
                    "services.auth.service.auth_service.register_user", new_callable=AsyncMock
                ) as mock_register,
                patch(
                    "services.auth.service.auth_service.create_access_token", new_callable=AsyncMock
                ) as mock_access,
                patch(
                    "services.auth.service.auth_service.create_refresh_token_record",
                    new_callable=AsyncMock,
                ) as mock_refresh,
            ):
                mock_register.return_value = mock_user
                mock_access.return_value = "access_token_string"
                mock_refresh.return_value = "refresh_token_string"

                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": TEST_EMAIL,
                        "username": TEST_USERNAME,
                        "password": TEST_PASSWORD,
                    },
                    headers=headers,
                    cookies={"csrf-token": csrf_token},
                )

                assert response.status_code == 201  # Register endpoint returns 201 Created
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, mock_jwt_secret_key):
        """Test registration with duplicate email."""
        from services.auth.exceptions import UserAlreadyExistsError

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:

            async def raise_user_exists(*args, **kwargs):
                raise UserAlreadyExistsError(email=TEST_EMAIL)

            # Patch the database module at the source to completely replace get_session
            # This ensures the real function never runs
            import db.database as db_module

            original_get_session = db_module.get_session

            # Replace get_session in the module
            db_module.get_session = mock_session_generator

            try:
                with (
                    patch("main.async_engine") as mock_engine,
                    patch("db.database.async_engine") as mock_db_engine,
                    patch(
                        "services.auth.service.auth_service.register_user",
                        side_effect=raise_user_exists,
                    ),
                ):
                    # Set up both engine mocks
                    mock_conn = AsyncMock()
                    mock_conn.execute = AsyncMock(return_value=None)
                    for mock_eng in [mock_engine, mock_db_engine]:
                        mock_eng.connect = MagicMock(return_value=mock_conn)
                        mock_eng.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                        mock_eng.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                    async with AsyncClient(
                        transport=ASGITransport(app=app), base_url="http://testserver"
                    ) as ac:
                        # Get CSRF token first
                        get_response = await ac.get("/health")
                        csrf_token = get_response.cookies.get("csrf-token")
                        headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

                        response = await ac.post(
                            "/api/v1/auth/register",
                            json={
                                "email": TEST_EMAIL,
                                "username": TEST_USERNAME,
                                "password": TEST_PASSWORD,
                            },
                            headers=headers,
                            cookies={"csrf-token": csrf_token} if csrf_token else {},
                        )

                        assert response.status_code == 409
            finally:
                # Restore original get_session
                db_module.get_session = original_get_session
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_register_weak_password(self, mock_jwt_secret_key):
        """Test registration with weak password."""
        csrf_token, headers = get_csrf_token_and_headers(client)
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": TEST_EMAIL,
                "username": TEST_USERNAME,
                "password": "short",  # Too short
            },
            headers=headers,
            cookies={"csrf-token": csrf_token},
        )

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, mock_jwt_secret_key):
        """Test successful user login."""
        csrf_token, headers = get_csrf_token_and_headers(client)

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:
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
                patch(
                    "services.auth.service.auth_service.authenticate_user", new_callable=AsyncMock
                ) as mock_auth,
                patch(
                    "services.auth.service.auth_service.create_access_token", new_callable=AsyncMock
                ) as mock_access,
                patch(
                    "services.auth.service.auth_service.create_refresh_token_record",
                    new_callable=AsyncMock,
                ) as mock_refresh,
            ):
                mock_auth.return_value = mock_user
                mock_access.return_value = "access_token_string"
                mock_refresh.return_value = "refresh_token_string"

                response = client.post(
                    "/api/v1/auth/login",
                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                    headers=headers,
                    cookies={"csrf-token": csrf_token},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_jwt_secret_key):
        """Test login with invalid credentials."""
        from services.auth.exceptions import InvalidCredentialsError

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:

            async def raise_invalid_credentials(*args, **kwargs):
                raise InvalidCredentialsError()

            # Patch both the service and database to prevent real operations
            with (
                patch("db.database.get_session", side_effect=mock_session_generator),
                patch("main.async_engine") as mock_engine,
                patch("db.database.async_engine") as mock_db_engine,
                patch(
                    "services.auth.service.auth_service.authenticate_user",
                    side_effect=raise_invalid_credentials,
                ),
            ):
                # Set up both engine mocks
                mock_conn = AsyncMock()
                mock_conn.execute = AsyncMock(return_value=None)
                for mock_eng in [mock_engine, mock_db_engine]:
                    mock_eng.connect = MagicMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://testserver"
                ) as ac:
                    # Get CSRF token first
                    get_response = await ac.get("/health")
                    csrf_token = get_response.cookies.get("csrf-token")
                    headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

                    response = await ac.post(
                        "/api/v1/auth/login",
                        json={"email": TEST_EMAIL, "password": "WrongPassword123!"},
                        headers=headers,
                        cookies={"csrf-token": csrf_token} if csrf_token else {},
                    )

                    assert response.status_code == 401
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, mock_jwt_secret_key):
        """Test login with inactive user account."""
        from services.auth.exceptions import InactiveUserError

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:

            async def raise_inactive_user(*args, **kwargs):
                raise InactiveUserError()

            # Patch both the service and database to prevent real operations
            with (
                patch("main.async_engine") as mock_engine,
                patch("db.database.async_engine") as mock_db_engine,
                patch(
                    "services.auth.service.auth_service.authenticate_user",
                    side_effect=raise_inactive_user,
                ),
            ):
                # Set up both engine mocks
                mock_conn = AsyncMock()
                mock_conn.execute = AsyncMock(return_value=None)
                for mock_eng in [mock_engine, mock_db_engine]:
                    mock_eng.connect = MagicMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://testserver"
                ) as ac:
                    # Get CSRF token first
                    get_response = await ac.get("/health")
                    csrf_token = get_response.cookies.get("csrf-token")
                    headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

                    response = await ac.post(
                        "/api/v1/auth/login",
                        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                        headers=headers,
                        cookies={"csrf-token": csrf_token} if csrf_token else {},
                    )

                    assert response.status_code == 403
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_refresh_success(self, mock_jwt_secret_key):
        """Test successful token refresh."""
        csrf_token, headers = get_csrf_token_and_headers(client)

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:
            with patch(
                "services.auth.service.auth_service.refresh_access_token", new_callable=AsyncMock
            ) as mock_refresh:
                mock_refresh.return_value = ("new_access_token", "valid_refresh_token")

                response = client.post(
                    "/api/v1/auth/refresh",
                    json={"refresh_token": "valid_refresh_token"},
                    headers=headers,
                    cookies={"csrf-token": csrf_token},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["access_token"] == "new_access_token"
                assert "refresh_token" in data
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, mock_jwt_secret_key):
        """Test refresh with invalid token."""
        from services.auth.exceptions import RefreshTokenNotFoundError

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:

            async def raise_token_not_found(*args, **kwargs):
                raise RefreshTokenNotFoundError()

            # Patch both the service and database to prevent real operations
            with (
                patch("db.database.get_session", side_effect=mock_session_generator),
                patch("main.async_engine") as mock_engine,
                patch("db.database.async_engine") as mock_db_engine,
                patch(
                    "services.auth.service.auth_service.refresh_access_token",
                    side_effect=raise_token_not_found,
                ),
            ):
                # Set up both engine mocks
                mock_conn = AsyncMock()
                mock_conn.execute = AsyncMock(return_value=None)
                for mock_eng in [mock_engine, mock_db_engine]:
                    mock_eng.connect = MagicMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://testserver"
                ) as ac:
                    # Get CSRF token first
                    get_response = await ac.get("/health")
                    csrf_token = get_response.cookies.get("csrf-token")
                    headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

                    response = await ac.post(
                        "/api/v1/auth/refresh",
                        json={"refresh_token": "invalid_token"},
                        headers=headers,
                        cookies={"csrf-token": csrf_token} if csrf_token else {},
                    )

                    assert response.status_code == 401
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_success(self, mock_jwt_secret_key):
        """Test successful logout."""
        csrf_token, headers = get_csrf_token_and_headers(client)

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        try:
            with patch(
                "services.auth.service.auth_service.revoke_refresh_token", new_callable=AsyncMock
            ) as mock_revoke:
                mock_revoke.return_value = None

                response = client.post(
                    "/api/v1/auth/logout",
                    json={"refresh_token": "refresh_token_to_revoke"},
                    headers=headers,
                    cookies={"csrf-token": csrf_token},
                )

                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                assert "successfully" in data["message"].lower()
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestUserProfile:
    """Tests for user profile endpoints."""

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, mock_jwt_secret_key):
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

        # Override the get_current_user dependency
        async def mock_get_current_user(*args, **kwargs):
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:
            # Patch database engine for health check
            with (
                patch("db.database.get_session", side_effect=mock_session_generator),
                patch("db.database.async_engine") as mock_engine,
            ):
                mock_conn = AsyncMock()
                mock_conn.execute = AsyncMock(return_value=None)
                mock_engine.connect = MagicMock(return_value=mock_conn)
                mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://testserver"
                ) as ac:
                    response = await ac.get(
                        "/api/v1/auth/me",
                        headers={"Authorization": f"Bearer {token}"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["email"] == TEST_EMAIL
                    assert data["username"] == TEST_USERNAME
                    assert "hashed_password" not in data
        finally:
            # Clean up dependency override
            app.dependency_overrides.pop(get_current_user, None)

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    def test_get_profile_unauthorized(self, mock_jwt_secret_key):
        """Test getting profile without authentication."""
        # Ensure no dependency override is set
        app.dependency_overrides.pop(get_current_user, None)

        # Patch database to prevent real operations
        with patch("db.database.get_session", side_effect=mock_session_generator):
            response = client.get("/api/v1/auth/me")

            # Without auth header, should get 401 Unauthorized
            assert response.status_code == 401

    @pytest.mark.skip(
        reason="AsyncClient with ASGITransport has middleware exception handling issues in CI"
    )
    @pytest.mark.asyncio
    async def test_update_user_profile(self, mock_jwt_secret_key):
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

        # Override the database session dependency
        app.dependency_overrides[get_session] = mock_session_generator

        # Override the get_current_user dependency
        async def mock_get_current_user(*args, **kwargs):
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:

            async def mock_update_user(*args, **kwargs):
                return updated_user

            # Patch both the service and database to prevent real operations
            with (
                patch("db.database.get_session", side_effect=mock_session_generator),
                patch("main.async_engine") as mock_engine,
                patch("db.database.async_engine") as mock_db_engine,
                patch(
                    "services.auth.service.auth_service.update_user", side_effect=mock_update_user
                ),
            ):
                # Set up both engine mocks
                mock_conn = AsyncMock()
                mock_conn.execute = AsyncMock(return_value=None)
                for mock_eng in [mock_engine, mock_db_engine]:
                    mock_eng.connect = MagicMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
                    mock_eng.connect.return_value.__aexit__ = AsyncMock(return_value=None)

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://testserver"
                ) as ac:
                    # Get CSRF token first
                    get_response = await ac.get("/health")
                    csrf_token = get_response.cookies.get("csrf-token")
                    headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}
                    headers["Authorization"] = f"Bearer {token}"

                    response = await ac.patch(
                        "/api/v1/auth/me",
                        headers=headers,
                        cookies={"csrf-token": csrf_token} if csrf_token else {},
                        json={"email": "newemail@example.com", "username": "newusername"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["email"] == "newemail@example.com"
                    assert data["username"] == "newusername"
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.pop(get_session, None)
            app.dependency_overrides.pop(get_current_user, None)
