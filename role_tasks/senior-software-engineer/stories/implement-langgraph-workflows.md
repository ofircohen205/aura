# Story: Implement LangGraph Workflows for "Struggle Detection" and "Code Audit"

**Role:** Senior Software Engineer
**Related SRS Section:** 3.1, 3.2, 4.1

## Desired Feature
The system needs an intelligent orchestration layer to handle stateful interactions for two key workflows:
1.  **Struggle Detection**: Analyzing sequences of edits to detect if a user is stuck.
2.  **Code Audit**: Performing static analysis and architectural checks on code changes.

This will be implemented using **LangGraph** to define state machines that can wait for user input, retry steps, and maintain context across turn-based interactions.

## Planning & Technical Spec

### Architecture
- **Framework**: LangGraph (built on top of LangChain).
- **State Definition**:
    - `StruggleState`: Inputs (edit frequency, error logs), History (previous attempts), Output (lesson recommendation).
    - `AuditState`: Inputs (diff, violation list), Output (pass/fail/remediation).
- **Nodes**:
    - `detect_struggle`: Analyzes input metrics (e.g., Levenshtein distance modification rate).
    - `generate_lesson`: Queries Vector Store for relevant content if struggle is confirmed.
    - `parse_diff`: Extracts context from Git diffs.
    - `check_violations`: Cross-references with "Golden Path" rules.

### Implementation Checklist
- [ ] Install dependencies: `langgraph`, `langchain`, `langchain-openai`.
- [ ] Define `StruggleGraph` class/workflow.
- [ ] Define `AuditGraph` class/workflow.
- [ ] Create API entry points (fastAPI routers) to trigger these graphs.
- [ ] Implement persistence (checkpointer) using Postgres to save workflow state (important for long-running audits).

## Testing Plan
- **Automated Tests**:
    - [ ] Unit tests for individual nodes (mocks for LLM calls).
    - [ ] Integration test running the full graph with a mock struggle scenario.
    - [ ] `pytest tests/workflows/test_struggle.py`
- **Manual Verification**:
    - [ ] Trigger the workflow via curl/Swagger UI with a sample "high frequency edit" event.
    - [ ] Verify the output contains a valid "Lesson" object.
