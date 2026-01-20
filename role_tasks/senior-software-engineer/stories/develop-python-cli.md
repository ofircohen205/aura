# Story: Develop Python CLI with Hook Integration

**GitHub Issue**: #1

**Role:** Senior Software Engineer
**Related SRS Section:** 1, 3.2, 4.2

## Desired Feature

The CLI is the guardian of the codebase. It needs to intercept Git commands (`commit`, `push`) and run local audits before allowing the action to proceed. It must be fast and reliable.

## Planning & Technical Spec

### Architecture

- **Library**: `Typer` (or `Click`).
- **Entry Point**: `aura`.
- **Commands**:
  - `aura hook install`: Sets up `.git/hooks`.
  - `aura audit --staged`: Runs checks on staged files.
  - `aura config`: Manages credentials.
- **Hook Strategy**:
  - `.git/hooks/pre-commit` -> calls `aura audit`.
  - Exit code 0 = Pass, 1 = Block.

### Standards & Workflows

- **Git Flow**: Create a new branch for this story and work only on that branch.
- **Issue Updates**: Reference the GitHub Issue (check header) in your commits and PRs.
- **Architecture**: Follow `docs/ARCHITECTURE.md` (CLI Architecture section).
- **New Commands**: Follow `docs/DEVELOPMENT.md` (Common Development Tasks section).

### Implementation Checklist

- [ ] Initialize Python Project (`poetry` or `pip`).
- [ ] Create `cli/main.py` with Typer app.
- [ ] Implement `install-hooks` command (writes shell script to `.git/hooks/pre-commit`).
- [ ] Implement `audit` command which acts as the runner.
- [ ] Create `ConfigManager` to read `~/.aura/config.yaml`.

## Testing Plan

- **Automated Tests**:
  - [ ] `pytest` for CLI commands (`typer.testing.CliRunner`).
  - [ ] Test config loading/saving.
- **Manual Verification**:
  - [ ] `pip install .` -> `aura --help`.
  - [ ] Run `aura hook install`.
  - [ ] Try to commit a file and verify the hook runs.
