"""
Integration Tests for Authentication Endpoints

Tests API endpoints with real database connections.
Requires database to be running.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.fixture(autouse=True)
async def reset_redis_clients():
    """
    Reset Redis clients before each test to avoid event loop issues.

    This ensures Redis clients are created fresh with the correct event loop
    for each test, preventing "got Future attached to a different loop" errors.
    """
    # Clean up any existing Redis clients before the test
    try:
        from services.redis import close_redis_clients

        await close_redis_clients()
    except Exception:
        # Don't fail if cleanup fails (e.g., no clients exist)
        pass

    yield

    # Clean up after test as well
    try:
        from services.redis import close_redis_clients

        await close_redis_clients()
    except Exception:
        # Don't fail if cleanup fails
        pass


@pytest.fixture
async def clean_test_users(init_test_db) -> AsyncGenerator[None]:
    """
    Clean up test users after each test.

    Note: We skip cleanup before test since we use unique_test_user_data
    which generates unique emails for each test, avoiding conflicts.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import select

    from db.database import async_engine
    from db.models.user import User

    yield

    # Clean up Redis clients first to avoid event loop issues
    try:
        from services.redis import close_redis_clients

        await close_redis_clients()
    except Exception:
        # Don't fail the test if Redis cleanup fails
        pass

    # Clean up after test only
    # Using unique user data means we don't need pre-test cleanup
    # Wrap in try/except to handle event loop closure and other errors gracefully
    try:
        async with AsyncSession(async_engine) as session:
            try:
                stmt = select(User).where(
                    (User.email == "test@example.com") | (User.email.like("test_%@example.com"))
                )
                result = await session.execute(stmt)
                users = result.scalars().all()
                for user in users:
                    await session.delete(user)
                await session.commit()
            except Exception:
                await session.rollback()
                # Don't fail the test if cleanup fails
                pass
    except (RuntimeError, OSError) as e:
        # Handle "Event loop is closed" and connection errors gracefully
        error_msg = str(e).lower()
        if any(
            phrase in error_msg
            for phrase in [
                "event loop is closed",
                "no running event loop",
                "connection",
                "closed",
            ]
        ):
            # Event loop or connection is closed, cleanup cannot proceed
            # This is acceptable for test cleanup
            pass
        else:
            # Re-raise other RuntimeErrors/OSErrors that we don't expect
            raise
    except Exception:
        # Don't fail the test if cleanup fails for any other reason
        pass


@pytest.fixture
def unique_test_user_data(test_user_data: dict[str, str]) -> dict[str, str]:
    """Generate unique test user data for each test."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": test_user_data["password"],
    }


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""

    async def test_register_endpoint(
        self, unique_test_user_data: dict[str, str], init_test_db, clean_test_users
    ):
        """Test user registration endpoint with real database."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            # Get CSRF token first
            get_response = await ac.get("/health")
            csrf_token = get_response.cookies.get("csrf-token")
            headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

            response = await ac.post(
                "/api/v1/auth/register",
                json=unique_test_user_data,
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )

            # Should succeed
            assert response.status_code == 201

    async def test_login_endpoint(
        self, unique_test_user_data: dict[str, str], init_test_db, clean_test_users
    ):
        """Test user login endpoint."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            # Get CSRF token first
            get_response = await ac.get("/health")
            csrf_token = get_response.cookies.get("csrf-token")
            headers = {"X-CSRF-Token": csrf_token} if csrf_token else {}

            # First register a user
            register_response = await ac.post(
                "/api/v1/auth/register",
                json=unique_test_user_data,
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )
            assert register_response.status_code == 201

            # Then try to login
            response = await ac.post(
                "/api/v1/auth/login",
                json={
                    "email": unique_test_user_data["email"],
                    "password": unique_test_user_data["password"],
                },
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )

            assert response.status_code == 200  # Should succeed

    async def test_get_current_user_requires_auth(self, init_test_db):
        """Test that /me endpoint requires authentication."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            # Make request without authorization header
            # This should return 401 before trying to access database
            response = await ac.get("/api/v1/auth/me", follow_redirects=False)

            # Should return 401 Unauthorized
            assert response.status_code == 401
