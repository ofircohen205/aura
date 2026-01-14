import pytest

from core_py.workflows.audit import AuditState, check_violations, parse_diff
from core_py.workflows.struggle import StruggleState, detect_struggle, generate_lesson


def test_detect_struggle_true():
    state = StruggleState(
        edit_frequency=15.0,
        error_logs=["Error 1"],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True


def test_detect_struggle_false():
    state = StruggleState(
        edit_frequency=5.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is False


def test_detect_struggle_boundary_edit_frequency():
    """Test boundary value: edit_frequency exactly at threshold."""
    # Exactly at threshold (10.0) should not trigger struggle
    state = StruggleState(
        edit_frequency=10.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is False

    # Just above threshold
    state["edit_frequency"] = 10.1
    result = detect_struggle(state)
    assert result["is_struggling"] is True


def test_detect_struggle_boundary_error_count():
    """Test boundary value: error_logs exactly at threshold."""
    # Exactly at threshold (2 errors) should not trigger struggle
    state = StruggleState(
        edit_frequency=5.0,
        error_logs=["Error 1", "Error 2"],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is False

    # Just above threshold (3 errors)
    state["error_logs"] = ["Error 1", "Error 2", "Error 3"]
    result = detect_struggle(state)
    assert result["is_struggling"] is True


def test_detect_struggle_extreme_values():
    """Test with extreme values."""
    # Very high edit frequency
    state = StruggleState(
        edit_frequency=1000.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True

    # Many errors
    state = StruggleState(
        edit_frequency=1.0,
        error_logs=[f"Error {i}" for i in range(100)],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True


@pytest.mark.asyncio
async def test_generate_lesson_struggling():
    state = StruggleState(
        edit_frequency=15.0,
        error_logs=[],
        history=[],
        is_struggling=True,
        lesson_recommendation=None,
    )
    result = await generate_lesson(state)
    assert result["lesson_recommendation"] is not None


@pytest.mark.asyncio
async def test_generate_lesson_not_struggling():
    """Test generate_lesson when not struggling."""
    state = StruggleState(
        edit_frequency=5.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )
    result = await generate_lesson(state)
    assert result["lesson_recommendation"] is None


def test_parse_diff():
    """Test parse_diff function with standard git unified diff format."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    print('hello')
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert isinstance(result, dict)
    assert "parsed_files" in result
    assert "parsed_hunks" in result
    assert "file_extensions" in result
    assert "added_lines" in result
    assert "removed_lines" in result
    assert len(result["parsed_files"]) > 0
    assert result["parsed_files"][0]["new_path"] == "src/file.py"
    assert "py" in result["file_extensions"]
    assert len(result["parsed_hunks"]) > 0
    assert result["added_lines"] > 0


def test_parse_diff_empty_string():
    """Test parse_diff with empty diff content."""
    state = AuditState(diff_content="", violations=[], status="pending")
    result = parse_diff(state)
    assert isinstance(result, dict)
    assert result["parsed_files"] == []
    assert result["parsed_hunks"] == []
    assert result["file_extensions"] == set()
    assert result["added_lines"] == 0
    assert result["removed_lines"] == 0


def test_parse_diff_multiple_files():
    """Test parse_diff with multiple files in diff."""
    diff_content = """--- a/src/file1.py
+++ b/src/file1.py
@@ -1,1 +1,1 @@
-old
+new
--- a/src/file2.py
+++ b/src/file2.py
@@ -1,1 +1,1 @@
-old2
+new2
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert len(result["parsed_files"]) == 2
    assert result["parsed_files"][0]["new_path"] == "src/file1.py"
    assert result["parsed_files"][1]["new_path"] == "src/file2.py"


def test_parse_diff_binary_file():
    """Test parse_diff with binary file detection."""
    diff_content = "Binary files a/image.png and b/image.png differ"
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert result["parsed_files"] == []
    assert result["parsed_hunks"] == []
    assert result["file_extensions"] == set()


def test_parse_diff_malformed():
    """Test parse_diff with malformed diff (graceful handling)."""
    diff_content = "This is not a valid diff format\n--- random text\n+++ more text"
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should not raise error, return empty or partial results
    assert isinstance(result, dict)
    assert "parsed_files" in result


@pytest.mark.asyncio
async def test_check_violations_fail():
    """Test check_violations with print statement (should fail)."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    print('hello')
"""
    # Need to parse diff first to get parsed_hunks
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"
    assert "violation_details" in result
    assert len(result["violation_details"]) > 0
    # Check that violation details have required fields
    detail = result["violation_details"][0]
    assert "file_path" in detail
    assert "line_number" in detail
    assert "severity" in detail
    assert "rule_name" in detail
    assert "message" in detail
    assert "remediation" in detail


@pytest.mark.asyncio
async def test_check_violations_pass():
    """Test check_violations with clean code (should pass)."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    return 'hello'
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) == 0
    assert result["status"] == "pass"


@pytest.mark.asyncio
async def test_check_violations_empty_diff():
    """Test check_violations with empty diff content."""
    state = AuditState(diff_content="", violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) == 0
    assert result["status"] == "pass"


@pytest.mark.asyncio
async def test_check_violations_multiple_prints():
    """Test check_violations with multiple print statements."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,4 +1,4 @@
 def foo():
-    pass
+    print('one')
+    print('two')
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"
    # Should detect multiple violations
    assert len(result["violation_details"]) >= 2


@pytest.mark.asyncio
async def test_check_violations_debugger_calls():
    """Test check_violations detects debugger calls."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    breakpoint()
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"
    # Check that it's a debugger violation
    assert any("debugger" in v.lower() for v in result["violations"])


@pytest.mark.asyncio
async def test_check_violations_hardcoded_secret():
    """Test check_violations detects hardcoded secrets."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    password = "secret123"
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)
    result = await check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"
    # Check that it's a secret violation
    assert any("password" in v.lower() or "secret" in v.lower() for v in result["violations"])
