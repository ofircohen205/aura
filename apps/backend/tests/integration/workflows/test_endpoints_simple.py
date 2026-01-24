"""
Simplified API integration tests for workflow endpoints.

Tests the workflow API v1 endpoints using the service layer.
"""

import sys
import time
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Add backend directory to path for conf import
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Add src directory to path for imports
SRC_DIR = Path(__file__).parent.parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import conf first to set up paths
import conf  # noqa: F401, E402

# Import the API v1 workflows app
from api.v1.workflows.endpoints import create_workflows_app  # noqa: E402

# Create a test app using the API v1 workflows app
test_app = create_workflows_app()


@pytest.mark.asyncio
async def test_trigger_struggle_workflow_simple():
    """Test triggering the struggle workflow via API."""
    # Mock the workflow service to avoid database dependency
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None  # Use None checkpointer
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post(
            "/struggle",
            json={"edit_frequency": 20.0, "error_logs": ["Error 1"], "history": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert "created_at" in data
        assert data["type"] == "Struggle Detection"
        assert data["state"]["is_struggling"] is True
        assert data["state"]["lesson_recommendation"] is not None


@pytest.mark.asyncio
async def test_trigger_struggle_workflow_not_struggling_simple():
    """Test triggering the struggle workflow when user is not struggling."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post(
            "/struggle",
            json={"edit_frequency": 5.0, "error_logs": [], "history": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert "created_at" in data
        assert data["type"] == "Struggle Detection"
        assert data["state"]["is_struggling"] is False
        assert data["state"]["lesson_recommendation"] is None


@pytest.mark.asyncio
async def test_trigger_audit_workflow_with_violations_simple():
    """Test triggering the audit workflow with code violations."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post(
            "/audit",
            json={
                "diff_content": """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    print('bad')
"""
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert "created_at" in data
        assert data["type"] == "Code Audit"
        assert data["state"]["status"] == "fail"  # Should fail due to print()
        assert len(data["state"]["violations"]) > 0


@pytest.mark.asyncio
async def test_trigger_audit_workflow_clean_code_simple():
    """Test triggering the audit workflow with clean code."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post(
            "/audit", json={"diff_content": "def foo():\n    return 'clean code'"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert data["status"] == "completed"
        assert "created_at" in data
        assert data["type"] == "Code Audit"
        assert data["state"]["status"] == "pass"
        assert len(data["state"]["violations"]) == 0


@pytest.mark.asyncio
async def test_trigger_struggle_workflow_invalid_input():
    """Test struggle workflow with invalid input (missing required field)."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        # Missing required field 'edit_frequency'
        response = client.post("/struggle", json={"error_logs": ["Error 1"]})
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_trigger_struggle_workflow_negative_frequency():
    """Test struggle workflow with negative edit frequency (should be rejected)."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post(
            "/struggle",
            json={"edit_frequency": -5.0, "error_logs": [], "history": []},
        )
        # Should be rejected by Pydantic validation (edit_frequency >= 0)
        assert response.status_code == 422
        assert "edit_frequency" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_trigger_audit_workflow_empty_diff():
    """Test audit workflow with empty diff content."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_get_checkpointer.return_value.__aenter__.return_value = None
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.post("/audit", json={"diff_content": ""})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["state"]["status"] == "pass"  # Empty diff should pass


@pytest.mark.asyncio
async def test_get_workflow_state_not_found():
    """Test get_workflow_state with non-existent thread_id."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_checkpointer_instance = AsyncMock()
        mock_checkpointer_instance.aget.return_value = None  # No checkpoint found
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer_instance
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        non_existent_id = str(uuid.uuid4())
        response = client.get(f"/workflows/{non_existent_id}")
        assert response.status_code == 404
        response_data = response.json()
        # API returns error response format with 'error' key containing 'message'
        assert "error" in response_data or "detail" in response_data


@pytest.mark.asyncio
async def test_get_workflow_state_success():
    """Test get_workflow_state with valid checkpoint."""
    with patch("services.workflows.service.get_checkpointer") as mock_get_checkpointer:
        mock_checkpointer_instance = AsyncMock()
        # Mock a valid checkpoint
        test_thread_id = str(uuid.uuid4())
        mock_checkpoint = {
            "channel_values": {
                "edit_frequency": 15.0,
                "is_struggling": True,
                "lesson_recommendation": "Test lesson",
            },
            "ts": time.time(),
        }
        mock_checkpointer_instance.aget.return_value = mock_checkpoint
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer_instance
        mock_get_checkpointer.return_value.__aexit__.return_value = None

        client = TestClient(test_app)
        response = client.get(f"/{test_thread_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == test_thread_id
        assert "state" in data
        assert "created_at" in data
        assert "type" in data
        assert data["type"] == "Struggle Detection"
        assert data["state"]["is_struggling"] is True
