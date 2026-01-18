"""
Unit Tests for Security Functions

Tests password hashing, JWT token creation, and other security utilities.
"""

from datetime import timedelta

from core.security import (
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
        secret_key = "test-secret-key"
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
