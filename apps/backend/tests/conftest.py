"""
Pytest Configuration and Shared Fixtures

Provides shared fixtures for all test types (unit, integration, e2e).
"""

import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402

# Test configuration
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
TEST_SECRET_KEY = "test-secret-key-for-jwt-tokens-minimum-32-chars"


@pytest.fixture(scope="session")
def jwt_secret_key() -> str:
    """JWT secret key for testing."""
    return TEST_SECRET_KEY


@pytest.fixture(autouse=True)
def mock_jwt_secret_key(monkeypatch, jwt_secret_key: str):
    """Set JWT secret key for testing."""
    monkeypatch.setenv("JWT_SECRET_KEY", jwt_secret_key)


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Mock Redis client for unit tests."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.setex = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.ping = AsyncMock(return_value=True)
    return mock_client


@pytest.fixture
def test_user_data() -> dict[str, str]:
    """Test user data for creating users."""
    return {
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }


@pytest.fixture
def app_client() -> TestClient:
    """FastAPI test client."""
    from main import app  # noqa: E402

    return TestClient(app)


# Integration test fixtures
@pytest.fixture
async def db_session() -> AsyncGenerator:
    """
    Real database session for integration tests.

    Note: Requires database to be running.
    """
    from db.database import get_session

    async for session in get_session():
        yield session
        break


# E2E test fixtures
@pytest.fixture
def api_base_url() -> str:
    """Base URL for API in e2e tests."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")
