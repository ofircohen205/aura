"""
API integration tests for workflow endpoints.
These tests work without a database by using None checkpointer.
For full integration with database, run tests in Docker environment.
"""

import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402
from main import app  # noqa: E402


@pytest.mark.asyncio
async def test_trigger_struggle_workflow():
    """Test triggering the struggle workflow via API."""
    # Mock the checkpointer where it's used in the service to avoid database dependency
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None  # Use None checkpointer
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.post(
                "/api/v1/workflows/workflows/struggle",
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
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.post(
                "/api/v1/workflows/workflows/struggle",
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
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.post(
                "/api/v1/workflows/workflows/audit",
                json={"diff_content": "def foo(): print('bad')"},
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
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.post(
                "/api/v1/workflows/workflows/audit",
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
    # Use a valid UUID format for the test
    non_existent_thread_id = str(uuid.uuid4())

    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        # Mock checkpointer to return None (no checkpoint found)
        mock_checkpointer_instance = AsyncMock()
        mock_checkpointer_instance.aget.return_value = None
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer_instance
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            response = await ac.get(f"/api/v1/workflows/workflows/{non_existent_thread_id}")

        # Without database, checkpoint won't be found
        assert response.status_code == 404
