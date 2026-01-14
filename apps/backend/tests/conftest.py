"""
Pytest Configuration and Fixtures

Shared test fixtures and configuration for backend tests.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401
from main import app

# Note: Full async database testing requires aiosqlite and proper SQLModel async support
# For now, we'll use mocks for database-dependent tests


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client
    """
    with TestClient(app) as test_client:
        yield test_client
