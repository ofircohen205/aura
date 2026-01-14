"""
API integration tests for workflow endpoints.
These tests work without a database by using None checkpointer.
For full integration with database, run tests in Docker environment.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401
from main import app


@pytest.mark.asyncio
async def test_trigger_struggle_workflow():
    """Test triggering the struggle workflow via API."""
    # Mock the checkpointer to avoid database dependency
    with patch("backend.routers.workflows.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None  # Use None checkpointer
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/workflows/struggle",
                json={"edit_frequency": 20.0, "error_logs": ["Error 1"], "history": []},
            )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert data["state"]["is_struggling"] is True
        assert data["state"]["lesson_recommendation"] is not None


@pytest.mark.asyncio
async def test_trigger_struggle_workflow_not_struggling():
    """Test triggering the struggle workflow when user is not struggling."""
    with patch("backend.routers.workflows.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/workflows/struggle",
                json={"edit_frequency": 5.0, "error_logs": [], "history": []},
            )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert data["state"]["is_struggling"] is False
        assert data["state"]["lesson_recommendation"] is None


@pytest.mark.asyncio
async def test_trigger_audit_workflow_with_violations():
    """Test triggering the audit workflow with code violations."""
    with patch("backend.routers.workflows.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/workflows/audit", json={"diff_content": "def foo(): print('bad')"}
            )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert data["state"]["status"] == "fail"  # Should fail due to print()
        assert len(data["state"]["violations"]) > 0


@pytest.mark.asyncio
async def test_trigger_audit_workflow_clean_code():
    """Test triggering the audit workflow with clean code."""
    with patch("backend.routers.workflows.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/workflows/audit",
                json={"diff_content": "def foo():\n    return 'clean code'"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert data["state"]["status"] == "pass"
        assert len(data["state"]["violations"]) == 0


@pytest.mark.asyncio
async def test_get_workflow_state_without_db():
    """Test getting workflow state (will return 404 without database)."""
    with patch("backend.routers.workflows.get_checkpointer") as mock_get_checkpointer:
        # Mock checkpointer to return None (no checkpoint found)
        mock_checkpointer_instance = AsyncMock()
        mock_checkpointer_instance.aget.return_value = None
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer_instance
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/workflows/non-existent-thread-id")

        # Without database, checkpoint won't be found
        assert response.status_code == 404
