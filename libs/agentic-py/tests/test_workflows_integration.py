"""
Integration tests for LangGraph workflows.
Tests the full graph execution with mocked checkpointer.
"""

import pytest

from agentic_py.workflows.audit import AuditState, build_audit_graph
from agentic_py.workflows.struggle import StruggleState, build_struggle_graph


@pytest.mark.asyncio
async def test_struggle_graph_full_workflow_struggling():
    """Test the full struggle graph workflow when user is struggling."""
    graph = build_struggle_graph(checkpointer=None)

    initial_state: StruggleState = {
        "edit_frequency": 15.0,
        "error_logs": ["Error 1", "Error 2"],
        "history": [],
        "is_struggling": False,
        "lesson_recommendation": None,
    }

    config = {"configurable": {"thread_id": "test-thread-1"}}
    final_state = await graph.ainvoke(initial_state, config=config)

    assert final_state["is_struggling"] is True
    assert final_state["lesson_recommendation"] is not None
    assert "state management" in final_state["lesson_recommendation"].lower()


@pytest.mark.asyncio
async def test_struggle_graph_full_workflow_not_struggling():
    """Test the full struggle graph workflow when user is not struggling."""
    graph = build_struggle_graph(checkpointer=None)

    initial_state: StruggleState = {
        "edit_frequency": 5.0,
        "error_logs": [],
        "history": [],
        "is_struggling": False,
        "lesson_recommendation": None,
    }

    config = {"configurable": {"thread_id": "test-thread-2"}}
    final_state = await graph.ainvoke(initial_state, config=config)

    assert final_state["is_struggling"] is False
    assert final_state["lesson_recommendation"] is None


@pytest.mark.asyncio
async def test_audit_graph_full_workflow_with_violations():
    """Test the full audit graph workflow with code violations."""
    graph = build_audit_graph(checkpointer=None)

    initial_state: AuditState = {
        "diff_content": """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    print('bad code')
""",
        "violations": [],
        "status": "pending",
    }

    config = {"configurable": {"thread_id": "test-thread-3"}}
    final_state = await graph.ainvoke(initial_state, config=config)

    assert len(final_state["violations"]) > 0
    assert final_state["status"] == "fail"
    assert any("print" in v.lower() for v in final_state["violations"])
    assert "violation_details" in final_state
    assert len(final_state["violation_details"]) > 0
    # Check parsed information is present
    assert "parsed_files" in final_state
    assert "parsed_hunks" in final_state


@pytest.mark.asyncio
async def test_audit_graph_full_workflow_clean_code():
    """Test the full audit graph workflow with clean code."""
    graph = build_audit_graph(checkpointer=None)

    initial_state: AuditState = {
        "diff_content": """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    return 'clean code'
""",
        "violations": [],
        "status": "pending",
    }

    config = {"configurable": {"thread_id": "test-thread-4"}}
    final_state = await graph.ainvoke(initial_state, config=config)

    assert len(final_state["violations"]) == 0
    assert final_state["status"] == "pass"
    assert "violation_details" in final_state
    assert len(final_state["violation_details"]) == 0
    # Check parsed information is present
    assert "parsed_files" in final_state
    assert "parsed_hunks" in final_state
