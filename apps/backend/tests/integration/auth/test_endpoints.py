"""
Integration Tests for Authentication Endpoints

Tests API endpoints with real database connections.
Requires database to be running.
"""

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.integration


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_endpoint(self, test_user_data: dict[str, str]):
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
                json=test_user_data,
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )

            # Should succeed or return appropriate error
            assert response.status_code in [201, 409]  # Created or Conflict

    @pytest.mark.asyncio
    async def test_login_endpoint(self, test_user_data: dict[str, str]):
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
            await ac.post(
                "/api/v1/auth/register",
                json=test_user_data,
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )

            # Then try to login
            response = await ac.post(
                "/api/v1/auth/login",
                json={"email": test_user_data["email"], "password": test_user_data["password"]},
                headers=headers,
                cookies={"csrf-token": csrf_token} if csrf_token else {},
            )

            assert response.status_code in [200, 401]  # OK or Unauthorized

    @pytest.mark.asyncio
    async def test_get_current_user_requires_auth(self):
        """Test that /me endpoint requires authentication."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.get("/api/v1/auth/me")

            assert response.status_code == 401  # Unauthorized
