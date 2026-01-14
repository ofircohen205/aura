import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Disable rate limiting for tests
os.environ["RATE_LIMIT_ENABLED"] = "false"

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402
from main import app  # noqa: E402

client = TestClient(app)


@patch("main.async_engine")
def test_health(mock_engine):
    """Test health check endpoint with mocked database connection."""
    # Mock async context manager for database connection
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value=None)

    # Mock the async context manager
    mock_engine.connect = MagicMock(return_value=mock_conn)
    mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"


def test_events_endpoint():
    response = client.post(
        "/api/v1/events/", json={"source": "pytest", "type": "test", "data": {"foo": "bar"}}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "received"


def test_audit_endpoint():
    response = client.get("/api/v1/audit/?repo_path=./")
    assert response.status_code == 200
    assert response.json()["status"] == "audit_started"
