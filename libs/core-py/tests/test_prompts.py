"""
Tests for prompt loading and template system.
"""

import pytest

from core_py.prompts.loader import get_prompt_path, load_prompt


def test_load_lesson_generation_prompt():
    """Test loading the lesson generation base prompt."""
    template = load_prompt("lesson_generation/lesson_generation_base")

    assert template is not None
    # Check that template has expected variables
    assert "edit_frequency" in template.template
    assert "error_logs" in template.template
    assert "history" in template.template
    assert "rag_context" in template.template


def test_load_violation_analysis_prompt():
    """Test loading the violation analysis base prompt."""
    template = load_prompt("violation_analysis/violation_analysis_base")

    assert template is not None
    # Check that template has expected variables
    assert "violation_details" in template.template
    assert "parsed_files" in template.template
    assert "diff_context" in template.template


def test_load_remediation_prompt():
    """Test loading the remediation suggestion prompt."""
    template = load_prompt("violation_analysis/remediation_suggestion")

    assert template is not None
    # Check that template has expected variables
    assert "file_path" in template.template
    assert "line_number" in template.template
    assert "violation_message" in template.template
    assert "violated_code" in template.template


def test_prompt_variable_substitution():
    """Test that prompts can be formatted with variables."""
    template = load_prompt("lesson_generation/lesson_generation_base")

    result = template.format(
        edit_frequency=15.0,
        error_logs="- TypeError: 'NoneType' object is not callable",
        history="- Tried using dict.get()",
        rag_context="No context available yet.",
    )

    assert "15.0" in result
    assert "TypeError" in result
    assert "dict.get()" in result


def test_get_prompt_path():
    """Test getting prompt file paths."""
    # Test with subdirectory
    path = get_prompt_path("lesson_generation/lesson_generation_base")
    assert path.exists()
    assert path.name == "lesson_generation_base.md"
    assert "lesson_generation" in str(path)

    # Test with violation analysis
    path = get_prompt_path("violation_analysis/violation_analysis_base")
    assert path.exists()
    assert path.name == "violation_analysis_base.md"
    assert "violation_analysis" in str(path)


def test_prompt_not_found():
    """Test error handling for missing prompts."""
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent/prompt")


def test_prompt_caching():
    """Test that prompts are cached (same instance returned)."""
    template1 = load_prompt("lesson_generation/lesson_generation_base")
    template2 = load_prompt("lesson_generation/lesson_generation_base")

    # Should be the same instance due to caching
    assert template1 is template2


def test_prompt_with_system_message():
    """Test that prompts with system messages are parsed correctly."""
    template = load_prompt("lesson_generation/lesson_generation_base")

    # The template should include system message content
    result = template.format(
        edit_frequency=10.0,
        error_logs="",
        history="",
        rag_context="",
    )

    # System message should be included in the formatted result
    assert len(result) > 0


def test_prompt_format_validation():
    """Test that prompt formatting validates required variables."""
    template = load_prompt("violation_analysis/remediation_suggestion")

    # Should raise error if required variables are missing
    with pytest.raises((KeyError, ValueError)):
        template.format(
            file_path="test.py",
            # Missing other required variables
        )


def test_prompt_with_all_variables():
    """Test formatting remediation prompt with all variables."""
    template = load_prompt("violation_analysis/remediation_suggestion")

    result = template.format(
        file_path="test.py",
        line_number=42,
        rule_name="no_print_statements",
        violation_message="Avoid using print statements",
        severity="error",
        violated_code="print('hello')",
        code_context="def foo():\n    print('hello')\n    return True",
    )

    assert "test.py" in result
    assert "42" in result
    assert "no_print_statements" in result
    assert "print('hello')" in result
