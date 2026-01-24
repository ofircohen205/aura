"""
Unit Tests for Security Functions

Tests password hashing, JWT token creation, and other security utilities.
"""

from datetime import timedelta

import pytest

pytestmark = pytest.mark.unit

from core.security import (  # noqa: E402
    create_jwt_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_jwt_token(self):
        """Test JWT token creation."""
        secret_key = "test-secret-key-for-jwt-tokens-minimum-32-chars"
        payload = {"sub": "user123", "email": "test@example.com"}

        token = create_jwt_token(
            payload=payload,
            secret_key=secret_key,
            expires_delta=timedelta(minutes=30),
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = create_refresh_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_jwt_token(self):
        """Test JWT token verification."""
        from core.security import verify_jwt_token

        secret_key = "test-secret-key-for-jwt-tokens-minimum-32-chars"
        payload = {"sub": "user123", "email": "test@example.com"}

        token = create_jwt_token(
            payload=payload,
            secret_key=secret_key,
            expires_delta=timedelta(minutes=30),
        )

        decoded = verify_jwt_token(token, secret_key)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"

    def test_verify_jwt_token_invalid(self):
        """Test JWT token verification with invalid token."""
        from core.security import verify_jwt_token

        secret_key = "test-secret-key-for-jwt-tokens-minimum-32-chars"
        decoded = verify_jwt_token("invalid_token", secret_key)
        assert decoded is None

    def test_verify_jwt_token_wrong_secret(self):
        """Test JWT token verification with wrong secret key."""
        from core.security import verify_jwt_token

        secret_key = "test-secret-key-for-jwt-tokens-minimum-32-chars"
        payload = {"sub": "user123"}

        token = create_jwt_token(
            payload=payload,
            secret_key=secret_key,
            expires_delta=timedelta(minutes=30),
        )

        decoded = verify_jwt_token(token, "wrong_secret_key")
        assert decoded is None
