# Story: Ensure PII/Secrets Scrubbing and Security Policies

**GitHub Issue**: #8

**Role:** Security Engineer
**Related SRS Section:** 4.3

## Desired Feature

Before any code diff is sent to the Cloud Backend (or LLM), it must be scrubbed of PII (Personall Identifiable Information) and Secrets (API Keys, Passwords). Additionally, we need to enforce security policies on the generated code audits.

## Planning & Technical Spec

### Architecture

- **Tooling**: `trufflehog` or `gitleaks` (for secret detection), `presidio` (Microsoft, for PII).
- **Integration Point**: The Python CLI (before sending payload) and the Backend (double-check).
- **Policy**: "Code Audit" workflow must flag any `subprocess.call` or SQL Injection risks.

### Standards & Workflows

- **Git Flow**: Create a new branch for this story and work only on that branch.
- **Issue Updates**: Reference the GitHub Issue (check header) in your commits and PRs.

### Implementation Checklist

- [ ] Evaluate and select a lightweight scrubbing library for the CLI (must be fast, <50ms overhead).
- [ ] Implement `ScrubberService` in the CLI.
- [ ] Define "Security Rules" for the LangGraph Audit workflow (e.g., "No hardcoded credentials").
- [ ] Review the `checks.yaml` configuration for the CLI.

## Testing Plan

- **Automated Tests**:
  - [ ] Unit test: Feed a string with a fake API key and ensure it is replaced with `[REDACTED]`.
- **Manual Verification**:
  - [ ] Create a commit with a dummy password.
  - [ ] Run `aura audit` and inspect the logs to ensure the password never left the machine.
