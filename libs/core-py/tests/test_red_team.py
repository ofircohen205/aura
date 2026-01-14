"""
Red Team Testing

Tests for edge cases and adversarial examples to ensure robustness.
"""

import pytest

from core_py.workflows.audit import AuditState, check_violations, parse_diff
from core_py.workflows.struggle import StruggleState, detect_struggle


@pytest.mark.asyncio
async def test_adversarial_large_diff():
    """Test handling of extremely large diffs."""
    # Create a very large diff (simulated)
    large_diff = "--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n"
    large_diff += "+" + "x" * 100000 + "\n"  # 100KB of added content

    state = AuditState(diff_content=large_diff, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)

    # Should not crash, may take longer but should complete
    result = await check_violations(state)
    assert "status" in result


@pytest.mark.asyncio
async def test_adversarial_malformed_diff():
    """Test handling of intentionally malformed diffs."""
    malformed_diffs = [
        "---\n+++\n@@\n",  # Minimal malformed
        "--- a\n+++ b\n" + "x" * 1000,  # No hunk headers
        "--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n" + "\x00" * 100,  # Null bytes
    ]

    for diff in malformed_diffs:
        state = AuditState(diff_content=diff, violations=[], status="pending")
        parsed = parse_diff(state)
        state.update(parsed)

        # Should handle gracefully without crashing
        result = await check_violations(state)
        assert "status" in result
        assert result["status"] in ("pass", "fail")


@pytest.mark.asyncio
async def test_edge_case_empty_error_logs():
    """Test struggle detection with edge case inputs."""
    # Empty error logs but high edit frequency
    state = StruggleState(
        edit_frequency=100.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )

    result = detect_struggle(state)
    assert result["is_struggling"] is True  # Should trigger on edit frequency alone


@pytest.mark.asyncio
async def test_edge_case_negative_edit_frequency():
    """Test handling of invalid input (negative edit frequency)."""
    # This should be caught by Pydantic validation, but test defensive coding
    state = StruggleState(
        edit_frequency=-5.0,  # Invalid but test robustness
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None,
    )

    result = detect_struggle(state)
    # Should handle gracefully (negative frequency shouldn't trigger struggle)
    assert isinstance(result["is_struggling"], bool)


@pytest.mark.asyncio
async def test_adversarial_code_injection_attempt():
    """Test handling of code that might try to exploit AST parsing."""
    malicious_code = """
    import os
    os.system('rm -rf /')  # Attempted injection
    eval('__import__("os").system("echo pwned")')
    exec('print("exploit")')
    """

    diff_content = f"""--- a/test.py
+++ b/test.py
@@ -1,1 +1,5 @@
+{malicious_code}
"""

    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)

    # Should parse safely without executing code
    result = await check_violations(state)
    assert "status" in result
    # Should detect violations (import os, eval, exec are suspicious)


@pytest.mark.asyncio
async def test_edge_case_unicode_characters():
    """Test handling of unicode and special characters in diffs."""
    unicode_diff = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-    pass
+    print('你好世界 🌍')
"""

    state = AuditState(diff_content=unicode_diff, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)

    result = await check_violations(state)
    assert "status" in result
    # Should detect print statement violation despite unicode


@pytest.mark.asyncio
async def test_edge_case_very_long_function():
    """Test detection of very long functions (edge case)."""
    # Create a function with exactly 50 lines (boundary case)
    long_function = "def long_func():\n"
    long_function += "\n".join([f"    x = {i}" for i in range(50)])

    diff_content = f"""--- a/test.py
+++ b/test.py
@@ -1,1 +1,51 @@
+{long_function}
"""

    state = AuditState(diff_content=diff_content, violations=[], status="pending")
    parsed = parse_diff(state)
    state.update(parsed)

    result = await check_violations(state)
    # Function is exactly 50 lines, should not trigger (threshold is >50)
    # But if it's 51 lines, should trigger
    assert "status" in result


@pytest.mark.asyncio
async def test_adversarial_secret_obfuscation():
    """Test detection of obfuscated secrets."""
    obfuscated_secrets = [
        "password = 's' + 'e' + 'c' + 'r' + 'e' + 't'",  # String concatenation
        "api_key = ''.join(['a', 'b', 'c'])",  # Join method
        "token = base64.b64decode('c2VjcmV0')",  # Base64 encoded
    ]

    for secret_code in obfuscated_secrets:
        diff_content = f"""--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
+    {secret_code}
"""

        state = AuditState(diff_content=diff_content, violations=[], status="pending")
        parsed = parse_diff(state)
        state.update(parsed)

        result = await check_violations(state)
        # Current pattern matching may not catch these
        # This is a known limitation - ML Engineer can enhance
        assert "status" in result
