"""
End-to-End Tests for Authentication Flow

Tests complete authentication flows from registration to token refresh.
These tests verify the entire system works together.
"""

import pytest

pytestmark = pytest.mark.e2e


class TestCompleteAuthFlow:
    """E2E tests for complete authentication flows."""

    def test_complete_registration_to_token_refresh_flow(
        self, app_client, test_user_data, jwt_secret_key
    ):
        """Test complete flow: register -> login -> refresh -> logout."""
        # 1. Register user
        register_response = app_client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201

        # 2. Login
        login_response = app_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 3. Get current user (with access token)
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = app_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200

        # 4. Refresh token
        refresh_response = app_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200

        # 5. Logout
        logout_response = app_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert logout_response.status_code == 200
