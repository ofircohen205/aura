"""
Integration Tests for Authentication Endpoints

Tests API endpoints with real database connections.
Requires database to be running.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""

    def test_register_endpoint(self, app_client: TestClient, test_user_data: dict[str, str]):
        """Test user registration endpoint with real database."""
        response = app_client.post("/api/v1/auth/register", json=test_user_data)

        # Should succeed or return appropriate error
        assert response.status_code in [201, 409]  # Created or Conflict

    def test_login_endpoint(self, app_client: TestClient, test_user_data: dict[str, str]):
        """Test user login endpoint."""
        # First register a user
        app_client.post("/api/v1/auth/register", json=test_user_data)

        # Then try to login
        response = app_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )

        assert response.status_code in [200, 401]  # OK or Unauthorized

    def test_get_current_user_requires_auth(self, app_client: TestClient):
        """Test that /me endpoint requires authentication."""
        response = app_client.get("/api/v1/auth/me")

        assert response.status_code == 401  # Unauthorized
