# Cursor Commands

This directory contains custom Cursor commands for the Aura project.

## Available Commands

### commit-and-push

Commit and push changes following the development pipeline conventions.

**Usage:**

- From Cursor: Open command palette (Cmd+Shift+P / Ctrl+Shift+P) and search for "commit-and-push"
- From terminal: `./scripts/commit-and-push.sh [options]`

**Options:**

- `--skip-ci`: Skip CI checks before committing
- `--fast-ci`: Run fast CI checks (skips tests and builds)

**Features:**

- Interactive prompts for commit type, scope, description, and Linear issue ID
- Validates commit message format: `<type>(<scope>): <description> [ISSUE-ID]`
- Optionally runs CI checks before committing
- Automatically stages, commits, and pushes changes
- Follows development pipeline conventions from `docs/workflows/development-pipeline.md`

**Example:**

```bash
# Interactive mode
./scripts/commit-and-push.sh

# Skip CI checks
./scripts/commit-and-push.sh --skip-ci

# Fast CI checks (no tests/builds)
./scripts/commit-and-push.sh --fast-ci
```

**Commit Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `docs`: Documentation changes
- `chore`: Maintenance tasks
