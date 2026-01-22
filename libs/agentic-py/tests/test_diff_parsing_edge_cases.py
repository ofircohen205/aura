"""
Tests for diff parsing edge cases and robustness.
"""

from agentic_py.workflows import AuditState
from agentic_py.workflows.audit import parse_diff


def test_parse_diff_merge_conflicts():
    """Test parsing diff with merge conflict markers."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,7 @@
 def foo():
+<<<<<<< HEAD
     return 'old'
+=======
+    return 'new'
+>>>>>>> branch
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should still parse despite merge conflicts
    assert isinstance(result, dict)
    assert "parsed_files" in result
    # Should log warning but continue parsing


def test_parse_diff_binary_file_null_bytes():
    """Test binary file detection with null bytes."""
    diff_content = "--- a/file.bin\n+++ b/file.bin\n\x00\x00\x00binary content"
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert result["parsed_files"] == []
    assert result["parsed_hunks"] == []
    assert result["file_extensions"] == set()


def test_parse_diff_binary_file_marker():
    """Test binary file detection with explicit marker."""
    diff_content = "Binary files a/image.png and b/image.png differ"
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert result["parsed_files"] == []
    assert result["parsed_hunks"] == []
    assert result["file_extensions"] == set()


def test_parse_diff_high_non_printable_ratio():
    """Test binary file detection based on non-printable character ratio."""
    # Create content with >10% non-printable characters
    diff_content = "--- a/file.bin\n+++ b/file.bin\n"
    diff_content += "normal text " * 10
    diff_content += "\x01\x02\x03\x04\x05" * 5  # Non-printable characters

    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should detect as binary
    assert result["parsed_files"] == []
    assert result["parsed_hunks"] == []


def test_parse_diff_context_format():
    """Test parsing context diff format (not just unified)."""
    diff_content = """*** a/src/file.py
--- b/src/file.py
***************
*** 1,3 ****
  def foo():
!     pass
--- 1,3 ----
  def foo():
!     return 'hello'
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should handle gracefully (may not parse perfectly but shouldn't crash)
    assert isinstance(result, dict)
    assert "parsed_files" in result


def test_parse_diff_no_file_headers():
    """Test parsing diff without file headers."""
    diff_content = "@@ -1,3 +1,3 @@\n-old\n+new"
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should handle gracefully
    assert isinstance(result, dict)
    assert "parsed_hunks" in result


def test_parse_diff_malformed_hunk_header():
    """Test parsing with malformed hunk header."""
    diff_content = """--- a/file.py
+++ b/file.py
@@ invalid hunk header @@
+some content
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should skip invalid hunk but continue
    assert isinstance(result, dict)
    assert "parsed_files" in result


def test_parse_diff_new_file():
    """Test parsing diff for new file (old path is /dev/null)."""
    diff_content = """--- /dev/null
+++ b/src/new_file.py
@@ -0,0 +1,3 @@
+def new_function():
+    return True
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert len(result["parsed_files"]) > 0
    assert result["parsed_files"][0]["new_path"] == "src/new_file.py"
    assert result["parsed_files"][0]["old_path"] is None


def test_parse_diff_deleted_file():
    """Test parsing diff for deleted file (new path is /dev/null)."""
    diff_content = """--- a/src/old_file.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_function():
-    return False
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert len(result["parsed_files"]) > 0
    assert result["parsed_files"][0]["old_path"] == "src/old_file.py"
    assert result["parsed_files"][0]["new_path"] is None


def test_parse_diff_multiple_hunks_same_file():
    """Test parsing diff with multiple hunks in same file."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    return 'hello'
@@ -10,3 +10,3 @@
 def bar():
-    pass
+    return 'world'
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert len(result["parsed_hunks"]) == 2
    assert result["parsed_hunks"][0]["file_path"] == "src/file.py"
    assert result["parsed_hunks"][1]["file_path"] == "src/file.py"


def test_parse_diff_whitespace_only():
    """Test parsing diff with whitespace-only changes."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    pass
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should parse successfully
    assert isinstance(result, dict)
    assert len(result["parsed_hunks"]) > 0


def test_parse_diff_unicode_content():
    """Test parsing diff with unicode characters."""
    diff_content = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    return 'old'
+    return 'новый'  # Russian text
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    assert isinstance(result, dict)
    assert len(result["parsed_hunks"]) > 0
    assert "новый" in result["parsed_hunks"][0]["added_lines"][0]


def test_parse_diff_very_long_line():
    """Test parsing diff with very long lines."""
    long_line = "x" * 10000
    diff_content = f"""--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    {long_line}
"""
    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    result = parse_diff(state)

    # Should handle long lines without crashing
    assert isinstance(result, dict)
    assert len(result["parsed_hunks"]) > 0
