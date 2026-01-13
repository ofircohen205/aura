import pytest
from core_py.workflows.struggle import detect_struggle, generate_lesson, StruggleState
from core_py.workflows.audit import parse_diff, check_violations, AuditState

def test_detect_struggle_true():
    state = StruggleState(
        edit_frequency=15.0,
        error_logs=["Error 1"],
        history=[],
        is_struggling=False,
        lesson_recommendation=None
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True

def test_detect_struggle_false():
    state = StruggleState(
        edit_frequency=5.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None
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
        lesson_recommendation=None
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
        lesson_recommendation=None
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
        lesson_recommendation=None
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True
    
    # Many errors
    state = StruggleState(
        edit_frequency=1.0,
        error_logs=[f"Error {i}" for i in range(100)],
        history=[],
        is_struggling=False,
        lesson_recommendation=None
    )
    result = detect_struggle(state)
    assert result["is_struggling"] is True

def test_generate_lesson_struggling():
    state = StruggleState(
        edit_frequency=15.0,
        error_logs=[],
        history=[],
        is_struggling=True,
        lesson_recommendation=None
    )
    result = generate_lesson(state)
    assert result["lesson_recommendation"] is not None

def test_generate_lesson_not_struggling():
    """Test generate_lesson when not struggling."""
    state = StruggleState(
        edit_frequency=5.0,
        error_logs=[],
        history=[],
        is_struggling=False,
        lesson_recommendation=None
    )
    result = generate_lesson(state)
    assert result["lesson_recommendation"] is None

def test_parse_diff():
    """Test parse_diff function (currently a placeholder)."""
    state = AuditState(
        diff_content="def foo():\n    return 'bar'",
        violations=[],
        status="pending"
    )
    result = parse_diff(state)
    # Currently returns empty dict, but should not raise errors
    assert isinstance(result, dict)

def test_parse_diff_empty_string():
    """Test parse_diff with empty diff content."""
    state = AuditState(
        diff_content="",
        violations=[],
        status="pending"
    )
    result = parse_diff(state)
    assert isinstance(result, dict)

def test_check_violations_fail():
    state = AuditState(
        diff_content="def foo():\n    print('hello')",
        violations=[],
        status="pending"
    )
    result = check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"

def test_check_violations_pass():
    state = AuditState(
        diff_content="def foo():\n    return 'hello'",
        violations=[],
        status="pending"
    )
    result = check_violations(state)
    assert len(result["violations"]) == 0
    assert result["status"] == "pass"

def test_check_violations_empty_diff():
    """Test check_violations with empty diff content."""
    state = AuditState(
        diff_content="",
        violations=[],
        status="pending"
    )
    result = check_violations(state)
    assert len(result["violations"]) == 0
    assert result["status"] == "pass"

def test_check_violations_multiple_prints():
    """Test check_violations with multiple print statements."""
    state = AuditState(
        diff_content="def foo():\n    print('one')\n    print('two')",
        violations=[],
        status="pending"
    )
    result = check_violations(state)
    assert len(result["violations"]) > 0
    assert result["status"] == "fail"
