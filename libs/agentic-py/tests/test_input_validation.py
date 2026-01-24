"""
Tests for input validation in API models and workflows.

Note: These tests require the backend app to be available in the Python path.
If running tests in isolation, these may need to be skipped or run with proper path setup.
"""

import pytest
from pydantic import ValidationError

# Try to import, skip tests if backend not available
try:
    from backend.routers.workflows import MAX_DIFF_CONTENT_LENGTH, AuditInput, StruggleInput
except ImportError:
    try:
        from apps.backend.src.backend.routers.workflows import (
            MAX_DIFF_CONTENT_LENGTH,
            AuditInput,
            StruggleInput,
        )
    except ImportError:
        pytest.skip("Backend app not available for testing", allow_module_level=True)


class TestStruggleInputValidation:
    """Tests for StruggleInput validation."""

    def test_struggle_input_valid(self):
        """Test valid struggle input."""
        inp = StruggleInput(
            edit_frequency=15.0,
            error_logs=["Error 1", "Error 2"],
            history=["Attempt 1"],
        )
        assert inp.edit_frequency == 15.0
        assert len(inp.error_logs) == 2
        assert len(inp.history) == 1

    def test_struggle_input_negative_frequency(self):
        """Test struggle input with negative edit frequency."""
        with pytest.raises(ValidationError):
            StruggleInput(edit_frequency=-5.0, error_logs=[], history=[])

    def test_struggle_input_defaults(self):
        """Test struggle input with default values."""
        inp = StruggleInput(edit_frequency=10.0)
        assert inp.error_logs == []
        assert inp.history == []

    def test_struggle_input_error_logs_validation(self):
        """Test error logs validation and sanitization."""
        # Test with too many error logs (should truncate)
        many_errors = [f"Error {i}" for i in range(150)]
        inp = StruggleInput(edit_frequency=10.0, error_logs=many_errors)

        # Should be truncated to 100
        assert len(inp.error_logs) == 100

    def test_struggle_input_error_logs_length_limit(self):
        """Test error log length truncation."""
        long_error = "x" * 2000  # Exceeds 1000 char limit
        inp = StruggleInput(edit_frequency=10.0, error_logs=[long_error])

        # Should be truncated
        assert len(inp.error_logs[0]) <= 1000
        assert "[truncated]" in inp.error_logs[0]


class TestAuditInputValidation:
    """Tests for AuditInput validation."""

    def test_audit_input_valid(self):
        """Test valid audit input."""
        diff = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
 def foo():
-    pass
+    return 'hello'
"""
        inp = AuditInput(diff_content=diff, violations=[])
        assert len(inp.diff_content) > 0
        assert inp.violations == []

    def test_audit_input_empty_diff(self):
        """Test audit input with empty diff."""
        inp = AuditInput(diff_content="", violations=[])
        assert inp.diff_content == ""

    def test_audit_input_max_length(self):
        """Test audit input with maximum length diff."""
        # Create diff at max length
        large_diff = "--- a/file.py\n+++ b/file.py\n" + "x" * (MAX_DIFF_CONTENT_LENGTH - 30)
        inp = AuditInput(diff_content=large_diff, violations=[])
        assert len(inp.diff_content) == MAX_DIFF_CONTENT_LENGTH - 30

    def test_audit_input_exceeds_max_length(self):
        """Test audit input exceeding maximum length."""
        # Create diff exceeding max length
        large_diff = "x" * (MAX_DIFF_CONTENT_LENGTH + 1)
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            AuditInput(diff_content=large_diff, violations=[])

    def test_audit_input_diff_format_validation(self):
        """Test diff format validation."""
        # Valid diff format
        valid_diff = """--- a/src/file.py
+++ b/src/file.py
@@ -1,3 +1,3 @@
"""
        inp = AuditInput(diff_content=valid_diff, violations=[])
        assert inp.diff_content == valid_diff

    def test_audit_input_invalid_diff_format(self):
        """Test diff format validation with invalid format."""
        # Diff without proper markers (should still validate but may log warning)
        invalid_diff = "This is not a valid git diff format"
        # Should not raise validation error, but may log warning
        inp = AuditInput(diff_content=invalid_diff, violations=[])
        assert inp.diff_content == invalid_diff

    def test_audit_input_defaults(self):
        """Test audit input with default values."""
        diff = "--- a/file.py\n+++ b/file.py\n"
        inp = AuditInput(diff_content=diff)
        assert inp.violations == []
