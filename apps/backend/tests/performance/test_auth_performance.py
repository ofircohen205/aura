"""
Performance Tests for Authentication System

Benchmarks and performance tests for authentication endpoints and operations.
"""

import time
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from db.models.user import User
from services.auth.service import AuthService

pytestmark = pytest.mark.performance


class TestAuthPerformance:
    """Performance tests for authentication operations."""

    @pytest.mark.asyncio
    async def test_password_hashing_performance(self):
        """Benchmark password hashing performance."""
        from core.security import hash_password

        password = "testpassword123"
        iterations = 10

        start_time = time.time()
        for _ in range(iterations):
            hash_password(password)
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations
        # Bcrypt with 12 rounds should take ~300-500ms per hash
        assert avg_time < 1.0, f"Password hashing too slow: {avg_time:.3f}s"

    @pytest.mark.asyncio
    async def test_jwt_token_creation_performance(self):
        """Benchmark JWT token creation performance."""
        from core.security import create_jwt_token

        secret_key = "test-secret-key-for-jwt-tokens-minimum-32-chars"
        payload = {"sub": "user123", "email": "test@example.com"}
        iterations = 100

        start_time = time.time()
        for _ in range(iterations):
            create_jwt_token(
                payload=payload,
                secret_key=secret_key,
            )
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations
        # JWT creation should be very fast (< 1ms per token)
        assert avg_time < 0.01, f"JWT creation too slow: {avg_time:.3f}s"

    @pytest.mark.asyncio
    async def test_bulk_user_creation_performance(self, auth_service: AuthService, mock_db_session):
        """Benchmark bulk user creation performance."""
        from unittest.mock import patch

        from dao.user import user_dao

        users_data = [
            {"email": f"user{i}@example.com", "username": f"user{i}", "password": "password123"}
            for i in range(10)
        ]

        with (
            patch.object(user_dao, "exists_by_email", return_value=False),
            patch.object(user_dao, "exists_by_username", return_value=False),
            patch.object(
                user_dao,
                "create",
                return_value=User(
                    id=uuid4(),
                    email="test@example.com",
                    username="test",
                    hashed_password="hashed",
                    is_active=True,
                    is_verified=False,
                    roles=["user"],
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ),
            ),
            patch("services.auth.service.hash_password", return_value="hashed"),
        ):
            start_time = time.time()
            created_users, errors = await auth_service.bulk_create_users(
                session=mock_db_session,
                users_data=users_data,
            )
            end_time = time.time()

            total_time = end_time - start_time
            # Bulk creation should handle 10 users in reasonable time
            assert total_time < 5.0, f"Bulk creation too slow: {total_time:.3f}s"
            assert len(created_users) == 10
