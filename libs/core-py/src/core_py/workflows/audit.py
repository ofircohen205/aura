"""
Code Audit Workflow

This module implements a LangGraph workflow for auditing code changes.
It parses diffs and checks for violations against coding standards.
"""

import ast
import logging
import re
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from core_py.ml.config import AUDIT_FUNCTION_LENGTH_THRESHOLD
from core_py.prompts.loader import load_prompt

logger = logging.getLogger(__name__)


class AuditState(TypedDict, total=False):
    """State for the Code Audit Workflow."""

    diff_content: str
    violations: list[str]
    status: str  # "pass", "fail", "remediation_required"
    parsed_files: list[dict[str, Any]]  # Parsed file information
    parsed_hunks: list[dict[str, Any]]  # Parsed diff hunks with metadata
    file_extensions: set[str]  # File extensions in diff
    added_lines: int  # Count of added lines
    removed_lines: int  # Count of removed lines
    violation_details: list[dict[str, Any]]  # Enhanced violation information


def validate_audit_state(state: AuditState) -> AuditState:
    """
    Validate and normalize audit state structure.

    Ensures required fields are present and have correct types.
    Provides default values for optional fields.

    Args:
        state: Audit state dictionary to validate

    Returns:
        Validated and normalized state dictionary

    Raises:
        ValueError: If state structure is invalid
    """
    validated = state.copy()

    # Ensure required fields have defaults
    if "diff_content" not in validated:
        validated["diff_content"] = ""
    if "violations" not in validated:
        validated["violations"] = []
    if "status" not in validated:
        validated["status"] = "pending"

    # Validate types
    if not isinstance(validated["diff_content"], str):
        raise ValueError("diff_content must be a string")
    if not isinstance(validated["violations"], list):
        raise ValueError("violations must be a list")
    if validated["status"] not in ("pass", "fail", "pending", "remediation_required"):
        raise ValueError(f"Invalid status: {validated['status']}")

    # Ensure optional fields have defaults if missing
    if "parsed_files" not in validated:
        validated["parsed_files"] = []
    if "parsed_hunks" not in validated:
        validated["parsed_hunks"] = []
    if "file_extensions" not in validated:
        validated["file_extensions"] = set()
    if "added_lines" not in validated:
        validated["added_lines"] = 0
    if "removed_lines" not in validated:
        validated["removed_lines"] = 0
    if "violation_details" not in validated:
        validated["violation_details"] = []

    return validated


def parse_diff(state: AuditState) -> AuditState:
    """
    Parses the diff content to extract structured information.

    Parses unified diff format to extract:
    - File paths (old and new)
    - Line numbers and hunks
    - Code blocks (added/removed lines)
    - File extensions for language-specific checks

    Args:
        state: Current workflow state with diff_content

    Returns:
        Updated state with parsed diff information
    """
    diff_content = state.get("diff_content", "")

    if not diff_content or not diff_content.strip():
        logger.debug("Empty diff content, returning empty parsed data")
        return {
            "parsed_files": [],
            "parsed_hunks": [],
            "file_extensions": set(),
            "added_lines": 0,
            "removed_lines": 0,
        }

    # Check for binary files - improved detection
    # Check for null bytes (common in binary files)
    # Check for explicit binary file markers
    # Check for very high ratio of non-printable characters
    is_binary = False
    if (
        "\x00" in diff_content
        or "Binary files" in diff_content
        or "binary file" in diff_content.lower()
    ):
        is_binary = True
    elif len(diff_content) > 100:
        # Check for high ratio of non-printable characters (excluding newlines and tabs)
        non_printable = sum(1 for c in diff_content if ord(c) < 32 and c not in "\n\r\t")
        if non_printable / len(diff_content) > 0.1:  # More than 10% non-printable
            is_binary = True

    # Check for merge conflict markers
    has_merge_conflicts = (
        "<<<<<<<" in diff_content or "=======" in diff_content or ">>>>>>>" in diff_content
    )

    if is_binary:
        logger.debug("Binary file detected in diff, skipping parsing")
        return {
            "parsed_files": [],
            "parsed_hunks": [],
            "file_extensions": set(),
            "added_lines": 0,
            "removed_lines": 0,
        }

    if has_merge_conflicts:
        logger.warning(
            "Merge conflict markers detected in diff, parsing may be incomplete",
            extra={"diff_length": len(diff_content)},
        )

    parsed_files: list[dict[str, Any]] = []
    parsed_hunks: list[dict[str, Any]] = []
    file_extensions: set[str] = set()
    total_added = 0
    total_removed = 0

    # Pattern for unified diff file header: --- a/path or +++ b/path
    file_header_pattern = re.compile(
        r"^---\s+(.+?)(?:\s+\d{4}-\d{2}-\d{2})?\s*$|^\+\+\+\s+(.+?)(?:\s+\d{4}-\d{2}-\d{2})?\s*$"
    )
    # Pattern for hunk header: @@ -old_start,old_count +new_start,new_count @@
    hunk_header_pattern = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")

    lines = diff_content.split("\n")
    current_file = None
    current_old_path = None
    current_new_path = None
    current_hunk = None
    in_hunk = False
    hunk_added_lines: list[str] = []
    hunk_removed_lines: list[str] = []

    for line in lines:
        # Check for file header (--- or +++)
        file_match = file_header_pattern.match(line)
        if file_match:
            if line.startswith("---"):
                current_old_path = file_match.group(1)
                # Remove a/ or b/ prefix if present
                if current_old_path.startswith("a/"):
                    current_old_path = current_old_path[2:]
                elif current_old_path.startswith("/dev/null"):
                    current_old_path = None
            elif line.startswith("+++"):
                current_new_path = file_match.group(2)
                # Remove a/ or b/ prefix if present
                if current_new_path.startswith("b/"):
                    current_new_path = current_new_path[2:]
                elif current_new_path.startswith("/dev/null"):
                    current_new_path = None

                # When we have both paths, create file entry
                if current_old_path or current_new_path:
                    file_path = current_new_path or current_old_path
                    if file_path:
                        ext = _extract_extension(file_path)
                        if ext:
                            file_extensions.add(ext)
                        parsed_files.append(
                            {
                                "old_path": current_old_path,
                                "new_path": current_new_path,
                                "extension": ext,
                            }
                        )
                        current_file = file_path
            continue

        # Check for hunk header
        hunk_match = hunk_header_pattern.match(line)
        if hunk_match:
            # Save previous hunk if exists
            if current_hunk is not None and in_hunk:
                current_hunk["added_lines"] = hunk_added_lines
                current_hunk["removed_lines"] = hunk_removed_lines
                parsed_hunks.append(current_hunk)

            try:
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse hunk header: {line}, error: {e}")
                continue

            current_hunk = {
                "file_path": current_file,
                "old_start": old_start,
                "old_count": old_count,
                "new_start": new_start,
                "new_count": new_count,
                "added_lines": [],
                "removed_lines": [],
            }
            hunk_added_lines = []
            hunk_removed_lines = []
            in_hunk = True
            continue

        # Process hunk content
        if in_hunk and current_hunk is not None:
            if line.startswith("+") and not line.startswith("+++"):
                # Added line (skip the + prefix, but not +++ file headers)
                content = line[1:]
                hunk_added_lines.append(content)
                total_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                # Removed line (skip the - prefix, but not --- file headers)
                content = line[1:]
                hunk_removed_lines.append(content)
                total_removed += 1
            elif line.startswith(" "):
                # Context line (unchanged), we can track if needed
                pass
            elif line.strip() == "":
                # Empty line in diff
                pass

    # Save last hunk if exists
    if current_hunk is not None and in_hunk:
        current_hunk["added_lines"] = hunk_added_lines
        current_hunk["removed_lines"] = hunk_removed_lines
        parsed_hunks.append(current_hunk)

    logger.info(
        "Diff parsing completed",
        extra={
            "files_count": len(parsed_files),
            "hunks_count": len(parsed_hunks),
            "added_lines": total_added,
            "removed_lines": total_removed,
            "extensions": list(file_extensions),
        },
    )

    return {
        "parsed_files": parsed_files,
        "parsed_hunks": parsed_hunks,
        "file_extensions": file_extensions,
        "added_lines": total_added,
        "removed_lines": total_removed,
    }


def _extract_extension(file_path: str) -> str | None:
    """
    Extract file extension from file path.

    Args:
        file_path: File path string

    Returns:
        File extension in lowercase, or None if no extension found
    """
    if not file_path:
        return None
    # Handle paths with dots (e.g., .github/workflows/file.yml)
    parts = file_path.split("/")
    filename = parts[-1]
    if "." in filename:
        return filename.split(".")[-1].lower()
    return None


async def check_violations(state: AuditState) -> AuditState:
    """
    Checks for violations in the code against coding standards.

    Uses AST parsing and rule-based detection to identify violations.
    ML Engineer optimizations:
    - Context-aware detection to reduce false positives
    - LLM-based analysis for ambiguous violations
    - Sensitivity tuning based on file type and context

    Args:
        state: Current workflow state with diff_content and parsed information

    Returns:
        Updated state with violations list, status, and violation details
    """
    violations = []
    violation_details = []
    diff_content = state.get("diff_content", "")
    parsed_hunks = state.get("parsed_hunks", [])
    parsed_files = state.get("parsed_files", [])

    # Get file extensions to determine which checks to run
    file_extensions = state.get("file_extensions", set())

    # Check Python files using AST parsing
    if "py" in file_extensions:
        violations_py, details_py = _check_python_violations(parsed_hunks, parsed_files)
        violations.extend(violations_py)
        violation_details.extend(details_py)

    # Basic pattern-based checks for all files
    violations_pattern, details_pattern = _check_pattern_violations(diff_content)
    violations.extend(violations_pattern)
    violation_details.extend(details_pattern)

    # Apply context-aware filtering to reduce false positives
    if violation_details:
        violation_details = await _filter_false_positives(
            violation_details, parsed_files, parsed_hunks, file_extensions
        )
        # Rebuild violations list from filtered details
        violations = [detail["message"] for detail in violation_details]

    status = "fail" if violations else "pass"

    logger.info(
        "Violation check completed",
        extra={
            "violation_count": len(violations),
            "status": status,
            "diff_length": len(diff_content),
            "files_checked": len(parsed_files),
        },
    )

    return {
        "violations": violations,
        "status": status,
        "violation_details": violation_details,
    }


def _check_python_violations(
    parsed_hunks: list[dict[str, Any]],
    parsed_files: list[dict[str, Any]],  # noqa: ARG001
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Check Python-specific violations using AST parsing.

    Args:
        parsed_hunks: List of parsed diff hunks
        parsed_files: List of parsed file information (reserved for future use)

    Returns:
        Tuple of (violations list, violation details list)
    """
    violations = []
    violation_details = []

    # Process each hunk that contains Python code
    for hunk in parsed_hunks:
        file_path = hunk.get("file_path", "unknown")
        added_lines = hunk.get("added_lines", [])

        # Combine added lines to form code blocks for AST parsing
        if not added_lines:
            continue

        code_block = "\n".join(added_lines)

        # Try to parse as Python code
        # Strip common leading whitespace to handle indented code blocks
        lines = code_block.split("\n")
        if lines:
            # Find minimum indentation (excluding empty lines)
            non_empty_lines = [line for line in lines if line.strip()]
            if non_empty_lines:
                min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                # Strip common indentation
                dedented_lines = [
                    line[min_indent:] if len(line) > min_indent else line for line in lines
                ]
                code_block_dedented = "\n".join(dedented_lines)
            else:
                code_block_dedented = code_block
        else:
            code_block_dedented = code_block

        # Try to parse as Python code
        parsed = False
        for attempt in [
            code_block_dedented,  # Try with dedented code
            code_block,  # Try as-is
            f"def _temp_check():\n{code_block}",  # Try wrapped in function
        ]:
            try:
                tree = ast.parse(attempt, filename=file_path)
                wrapped = attempt.startswith("def _temp_check()")
                violations_ast, details_ast = _check_ast_violations(tree, file_path, hunk, wrapped)
                violations.extend(violations_ast)
                violation_details.extend(details_ast)
                parsed = True
                break
            except SyntaxError:
                continue
            except Exception as e:
                logger.warning(f"Error parsing Python AST for {file_path}: {e}")
                break

        if not parsed:
            # Not valid Python syntax, skip AST checks but do pattern checks
            logger.debug(f"Could not parse as Python AST: {file_path}")

    return violations, violation_details


def _check_ast_violations(
    tree: ast.AST, file_path: str, hunk: dict[str, Any], wrapped_in_function: bool = False
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Check violations using AST analysis.

    Args:
        tree: Parsed AST tree
        file_path: Path to the file
        hunk: Hunk information with line numbers
        wrapped_in_function: Whether the code was wrapped in a function for parsing

    Returns:
        Tuple of (violations list, violation details list)
    """
    new_start = hunk.get("new_start", 1)

    class ViolationVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []
            self.details = []
            # If wrapped in function, offset by 1 for the function definition line
            self.line_offset = new_start - (2 if wrapped_in_function else 1)

        def visit_Call(self, node):
            # Check for print statements
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                line_no = node.lineno + self.line_offset
                msg = "Avoid using print statements in production code. Use logging instead."
                self.violations.append(msg)
                self.details.append(
                    {
                        "file_path": file_path,
                        "line_number": line_no,
                        "severity": "error",
                        "rule_name": "no_print_statements",
                        "message": msg,
                        "remediation": "Replace print() with logger.debug() or logger.info()",
                    }
                )

            # Check for debugger calls
            if isinstance(node.func, ast.Name) and node.func.id in ("pdb", "ipdb", "breakpoint"):
                line_no = node.lineno + self.line_offset
                msg = f"Avoid using {node.func.id} debugger calls in production code."
                self.violations.append(msg)
                self.details.append(
                    {
                        "file_path": file_path,
                        "line_number": line_no,
                        "severity": "error",
                        "rule_name": "no_debugger_calls",
                        "message": msg,
                        "remediation": "Remove debugger calls before committing",
                    }
                )

            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            # Check for long functions (threshold configurable via AUDIT_FUNCTION_LENGTH_THRESHOLD)
            if hasattr(node, "end_lineno") and node.end_lineno:
                function_length = node.end_lineno - node.lineno
                if function_length > AUDIT_FUNCTION_LENGTH_THRESHOLD:
                    line_no = node.lineno + self.line_offset
                    msg = f"Function '{node.name}' is too long ({function_length} lines). Consider breaking it into smaller functions."
                    self.violations.append(msg)
                    self.details.append(
                        {
                            "file_path": file_path,
                            "line_number": line_no,
                            "severity": "warning",
                            "rule_name": "long_function",
                            "message": msg,
                            "remediation": "Break function into smaller, focused functions",
                        }
                    )

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            # Same check for async functions (threshold configurable via AUDIT_FUNCTION_LENGTH_THRESHOLD)
            if hasattr(node, "end_lineno") and node.end_lineno:
                function_length = node.end_lineno - node.lineno
                if function_length > AUDIT_FUNCTION_LENGTH_THRESHOLD:
                    line_no = node.lineno + self.line_offset
                    msg = f"Async function '{node.name}' is too long ({function_length} lines). Consider breaking it into smaller functions."
                    self.violations.append(msg)
                    self.details.append(
                        {
                            "file_path": file_path,
                            "line_number": line_no,
                            "severity": "warning",
                            "rule_name": "long_function",
                            "message": msg,
                            "remediation": "Break function into smaller, focused functions",
                        }
                    )

            self.generic_visit(node)

    visitor = ViolationVisitor()

    # If wrapped in function, visit the function body instead of the whole tree
    if wrapped_in_function and isinstance(tree, ast.Module) and len(tree.body) > 0:
        if isinstance(tree.body[0], ast.FunctionDef | ast.AsyncFunctionDef):
            # Visit the function body
            for node in tree.body[0].body:
                visitor.visit(node)
        else:
            visitor.visit(tree)
    else:
        visitor.visit(tree)

    return visitor.violations, visitor.details


def _check_pattern_violations(diff_content: str) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Check violations using pattern matching (regex).

    This provides basic pattern-based checks that work across all file types.
    ML Engineer will enhance with more sophisticated patterns.

    Args:
        diff_content: Full diff content

    Returns:
        Tuple of (violations list, violation details list)
    """
    violations = []
    violation_details = []

    # Check for hardcoded secrets (basic patterns)
    # ML Engineer will optimize these patterns
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
        (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token detected"),
    ]

    lines = diff_content.split("\n")
    for line_num, line in enumerate(lines, start=1):
        # Only check added lines (lines starting with +)
        # Skip diff metadata lines (+++ file paths)
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:]  # Remove + prefix
            for pattern, message in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(message)
                    violation_details.append(
                        {
                            "file_path": "unknown",  # Would need file context from parsed diff
                            "line_number": line_num,
                            "severity": "error",
                            "rule_name": "hardcoded_secret",
                            "message": message,
                            "remediation": "Use environment variables or secure secret management",
                        }
                    )
                    break  # Only report once per line

    return violations, violation_details


async def _filter_false_positives(
    violation_details: list[dict[str, Any]],
    parsed_files: list[dict[str, Any]],  # noqa: ARG001
    parsed_hunks: list[dict[str, Any]],  # noqa: ARG001
    file_extensions: set[str],  # noqa: ARG001
) -> list[dict[str, Any]]:
    """
    Filter false positives using context-aware heuristics and LLM analysis.

    This function applies multiple strategies to reduce false positives:
    1. File type context (test files, config files may have different rules)
    2. Code context analysis
    3. LLM-based ambiguity resolution for edge cases (with batching for efficiency)

    Args:
        violation_details: List of detected violations
        parsed_files: List of parsed file information
        parsed_hunks: List of parsed diff hunks
        file_extensions: Set of file extensions

    Returns:
        Filtered list of violations with false positives removed
    """
    from core_py.ml.batching import batch_llm_calls
    from core_py.ml.config import LLM_ENABLED
    from core_py.prompts.loader import load_prompt

    filtered = []
    violations_needing_llm = []

    # First pass: apply heuristics that don't require LLM
    for violation in violation_details:
        file_path = violation.get("file_path", "unknown")
        rule_name = violation.get("rule_name", "")

        # Context-aware filtering heuristics
        should_keep = True

        # Skip violations in test files for certain rules (e.g., print statements in tests are OK)
        if _is_test_file(file_path) and rule_name in ("no_print_statements",):
            logger.debug(f"Filtering violation in test file: {file_path}, rule: {rule_name}")
            should_keep = False
        # Config files need LLM analysis - collect for batching
        elif _is_config_file(file_path) and rule_name == "hardcoded_secret" and LLM_ENABLED:
            violations_needing_llm.append((violation, file_path))
            continue  # Will be processed in batch
        else:
            # Keep all other violations
            filtered.append(violation)

    # Batch process violations that need LLM analysis
    if violations_needing_llm and LLM_ENABLED:
        try:
            # Load prompt template once
            prompt_template = load_prompt("violation_analysis/violation_analysis_ambiguous")

            # Generate prompts for all violations needing analysis
            prompts = []
            for violation, file_path in violations_needing_llm:
                code_context = violation.get("code_context", "Code context not available")
                formatted_prompt = prompt_template.format(
                    violation_message=violation.get("message", ""),
                    file_path=file_path,
                    line_number=violation.get("line_number", 0),
                    rule_name=violation.get("rule_name", "unknown"),
                    code_context=code_context,
                    file_extension=file_path.split(".")[-1] if "." in file_path else "unknown",
                    project_context="Python project with standard coding practices",
                )
                prompts.append(formatted_prompt)

            # Batch process LLM calls
            analyses = await batch_llm_calls(prompts)

            # Process results
            for (violation, file_path), analysis in zip(
                violations_needing_llm, analyses, strict=False
            ):
                analysis_upper = analysis.upper()
                if "FLAGGED" in analysis_upper:
                    logger.debug(f"LLM analysis: Keep violation in {file_path}")
                    filtered.append(violation)
                elif "IGNORED" in analysis_upper:
                    logger.debug(f"LLM analysis: Filter violation in {file_path} (false positive)")
                    # Don't add to filtered (filtered out)
                else:
                    # Default to keeping if unclear
                    logger.warning(f"LLM analysis unclear for {file_path}, keeping violation")
                    filtered.append(violation)

        except Exception as e:
            logger.error(
                f"Batch LLM analysis failed, falling back to individual analysis: {e}",
                exc_info=True,
            )
            # Fallback to individual analysis
            for violation, file_path in violations_needing_llm:
                should_keep = await _analyze_ambiguous_violation(violation, file_path)
                if should_keep:
                    filtered.append(violation)

    logger.debug(
        f"Filtered {len(violation_details)} violations to {len(filtered)} after false positive filtering"
    )

    return filtered


def _is_test_file(file_path: str) -> bool:
    """Check if file is a test file."""
    test_indicators = ["test_", "_test", "/tests/", "/test/"]
    return any(indicator in file_path.lower() for indicator in test_indicators)


def _is_config_file(file_path: str) -> bool:
    """Check if file is a configuration file."""
    config_indicators = [".config.", "config/", ".env", "settings.", "conf."]
    return any(indicator in file_path.lower() for indicator in config_indicators)


async def _analyze_ambiguous_violation(violation: dict[str, Any], file_path: str) -> bool:
    """
    Use LLM to analyze ambiguous violations and determine if they should be flagged.

    Args:
        violation: Violation detail dictionary
        file_path: Path to the file

    Returns:
        True if violation should be kept, False if it's a false positive
    """
    from core_py.ml.config import LLM_ENABLED
    from core_py.ml.llm import invoke_llm_with_retry

    if not LLM_ENABLED:
        # Default to keeping violations if LLM is not enabled
        return True

    try:
        # Load the ambiguous violation analysis prompt
        prompt_template = load_prompt("violation_analysis/violation_analysis_ambiguous")

        # Get code context from violation
        code_context = violation.get("code_context", "")
        if not code_context:
            # Try to extract from parsed hunks if available
            code_context = "Code context not available"

        # Format prompt
        formatted_prompt = prompt_template.format(
            violation_message=violation.get("message", ""),
            file_path=file_path,
            line_number=violation.get("line_number", 0),
            rule_name=violation.get("rule_name", "unknown"),
            code_context=code_context,
            file_extension=file_path.split(".")[-1] if "." in file_path else "unknown",
            project_context="Python project with standard coding practices",
        )

        # Call LLM for analysis with retry logic
        analysis = await invoke_llm_with_retry(formatted_prompt)

        # Parse LLM response to determine if violation should be kept
        # Look for "FLAGGED" or "IGNORED" in response
        analysis_upper = analysis.upper()
        if "FLAGGED" in analysis_upper:
            logger.debug(f"LLM analysis: Keep violation in {file_path}")
            return True
        elif "IGNORED" in analysis_upper:
            logger.debug(f"LLM analysis: Filter violation in {file_path} (false positive)")
            return False
        else:
            # Default to keeping if unclear
            logger.warning(f"LLM analysis unclear for {file_path}, keeping violation")
            return True

    except RuntimeError as e:
        # LLM disabled or quota/auth errors - default to keeping violation
        logger.warning(
            f"LLM analysis unavailable for {file_path}, defaulting to keep violation: {e}"
        )
        return True
    except Exception as e:
        logger.error(
            f"Failed to analyze ambiguous violation with LLM: {e}",
            extra={"file_path": file_path, "rule_name": violation.get("rule_name")},
            exc_info=True,
        )
        # Default to keeping violation if LLM analysis fails
        return True


async def analyze_violations_with_llm(
    violation_details: list[dict[str, Any]],
    parsed_files: list[dict[str, Any]],
    diff_content: str,
    file_extensions: set[str],
) -> dict[str, Any]:
    """
    Analyze violations using LLM-based prompt templates.

    WARNING: This function is not yet implemented and will raise NotImplementedError.
    This is a placeholder for future ML integration.

    Args:
        violation_details: List of violation detail dictionaries
        parsed_files: List of parsed file information
        diff_content: Full diff content
        file_extensions: Set of file extensions in the diff

    Returns:
        Dictionary with LLM analysis results

    Raises:
        NotImplementedError: This function is not yet implemented

    Note:
        This function should be implemented using `invoke_llm_with_retry()` from
        `core_py.ml.llm` when LLM-based violation analysis is needed.
    """
    raise NotImplementedError(
        "analyze_violations_with_llm() is not yet implemented. "
        "This function requires LLM integration for batch violation analysis. "
        "For now, use the rule-based violation detection in check_violations()."
    )


async def generate_remediation(
    violation_detail: dict[str, Any], code_context: str, violated_code: str
) -> dict[str, Any]:
    """
    Generate remediation suggestions using LLM-based prompt templates.

    This function uses LLM to generate personalized remediation suggestions for code violations.
    It loads the remediation suggestion prompt template and calls the LLM with retry logic.

    Args:
        violation_detail: Single violation detail dictionary
        code_context: Surrounding code context
        violated_code: The specific code that violates the rule

    Returns:
        Dictionary with remediation suggestions:
        - remediation_complete (bool): Whether LLM generation succeeded
        - suggestion (str): Generated remediation suggestion or fallback message
        - message (str, optional): Status message if LLM is disabled
        - error (str, optional): Error message if generation failed

    Note:
        Requires LLM_ENABLED=true and valid OPENAI_API_KEY to generate suggestions.
        Falls back to manual review message if LLM is unavailable.
    """
    try:
        # Load the remediation suggestion prompt template
        prompt_template = load_prompt("violation_analysis/remediation_suggestion")

        # Format the prompt with violation data
        formatted_prompt = prompt_template.format(
            file_path=violation_detail.get("file_path", "unknown"),
            line_number=violation_detail.get("line_number", 0),
            rule_name=violation_detail.get("rule_name", "unknown"),
            violation_message=violation_detail.get("message", ""),
            severity=violation_detail.get("severity", "error"),
            violated_code=violated_code,
            code_context=code_context,
        )

        # Log formatted prompt length for debugging
        logger.debug(f"Formatted remediation prompt length: {len(formatted_prompt)}")

        # Call LLM for remediation generation with retry logic
        from core_py.ml.config import LLM_ENABLED
        from core_py.ml.llm import invoke_llm_with_retry

        if LLM_ENABLED:
            try:
                remediation = await invoke_llm_with_retry(formatted_prompt)

                logger.info("Remediation generated with LLM")

                return {
                    "remediation_complete": True,
                    "suggestion": remediation,
                }
            except RuntimeError as e:
                logger.warning(f"LLM remediation generation unavailable: {e}")
            except Exception as e:
                logger.error(f"LLM remediation generation failed: {e}", exc_info=True)

        logger.debug("Remediation prompt loaded (LLM disabled or failed)")

        return {
            "remediation_complete": False,
            "message": "LLM integration disabled or failed - enable LLM_ENABLED=true",
            "suggestion": violation_detail.get("remediation", "Manual review required"),
        }

    except Exception as e:
        logger.error(
            "Failed to generate remediation",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "violation_rule": violation_detail.get("rule_name", "unknown"),
            },
            exc_info=True,
        )
        return {
            "remediation_complete": False,
            "error": str(e),
            "suggestion": violation_detail.get("remediation", "Manual review required"),
        }


def build_audit_graph(checkpointer=None):
    workflow = StateGraph(AuditState)

    workflow.add_node("parse_diff", parse_diff)
    workflow.add_node("check_violations", check_violations)

    workflow.set_entry_point("parse_diff")
    workflow.add_edge("parse_diff", "check_violations")
    workflow.add_edge("check_violations", END)

    return workflow.compile(checkpointer=checkpointer)
