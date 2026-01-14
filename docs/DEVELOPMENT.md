# Development Setup

This document describes how to set up the development environment for the Aura project.

## Prerequisites

- Python 3.13+
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) for Python package management
- npm for Node.js package management

## Initial Setup

### 1. Install Python Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all Python dependencies
uv sync --all-groups --dev
```

### 2. Install Node.js Dependencies

```bash
npm install
```

### 3. Install Pre-commit Hooks

Pre-commit hooks ensure code quality by running linters, formatters, and other checks before commits.

```bash
# Install pre-commit (if not already installed via uv sync)
uv run pip install pre-commit

# Install the git hooks
uv run pre-commit install

# Or install hooks for all supported hooks (including commit-msg)
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg
```

## Code Quality Tools

### Python

The project uses the following tools for Python code quality:

- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **Bandit**: Security linter

#### Running Python Linters

```bash
# Run ruff linting
uv run ruff check apps/backend libs/core-py clients/cli

# Auto-fix linting issues
uv run ruff check --fix apps/backend libs/core-py clients/cli

# Run ruff formatting
uv run ruff format apps/backend libs/core-py clients/cli

# Check formatting without making changes
uv run ruff format --check apps/backend libs/core-py clients/cli

# Run mypy type checking
uv run mypy apps/backend libs/core-py clients/cli
```

### TypeScript/JavaScript

The project uses the following tools for TypeScript/JavaScript code quality:

- **ESLint**: JavaScript and TypeScript linter
- **Prettier**: Code formatter

#### Running TypeScript/JavaScript Linters

```bash
# Run ESLint
npm run lint

# Auto-fix ESLint issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting without making changes
npm run format:check

# Run TypeScript type checking
npm run type-check
```

## Pre-commit Hooks

Pre-commit hooks automatically run on every commit. They check:

- Trailing whitespace and end-of-file fixes
- YAML, JSON, and TOML syntax
- Python formatting (ruff format)
- Python linting (ruff)
- Python type checking (mypy)
- TypeScript/JavaScript formatting (Prettier)
- TypeScript/JavaScript linting (ESLint)
- Security checks (Bandit)
- Dockerfile linting (hadolint)

### Running Pre-commit Manually

You can run pre-commit hooks manually on all files:

```bash
uv run pre-commit run --all-files
```

Or on specific files:

```bash
uv run pre-commit run --files path/to/file.py
```

## CI Checks Before Committing

Before committing, you should run the CI check script to ensure your code will pass GitHub Actions CI. This script runs the same checks as the CI pipeline locally.

### Running CI Checks

Run all CI checks (lint, type check, tests, and builds):

```bash
# Using the script directly
./scripts/ci-check.sh

# Or using just
just ci-check
```

Run CI checks without tests and builds (faster for quick validation):

```bash
just ci-check-fast
# or
./scripts/ci-check.sh --skip-tests --skip-build
```

The CI check script runs:

1. **Python lint and type check**: ruff lint, ruff format check, mypy
2. **Python tests**: backend and core-py tests
3. **Python build**: Builds all Python packages
4. **TypeScript lint and type check**: ESLint and TypeScript type checking
5. **TypeScript build**: Builds all TypeScript projects
6. **TypeScript tests**: Runs all TypeScript tests

**Note**: The CI workflow (`.github/workflows/ci.yml`) runs automatically on all branch pushes and pull requests, so running this script before committing helps catch issues early.

## Running Tests

### Python Tests

```bash
# Run all Python tests
cd apps/backend && uv run pytest tests/ -v
cd libs/core-py && uv run pytest tests/ -v

# Run tests for a specific project from root
uv run --directory apps/backend pytest tests/ -v
```

### TypeScript/JavaScript Tests

```bash
# Run all tests
npm run test --workspaces

# Run tests for a specific workspace
cd apps/web-dashboard && npm test
```

## CI/CD

The project uses GitHub Actions for continuous integration. The main CI pipeline (`ci.yml`) runs:

1. **Python lint and type check**:
   - Lints Python code with ruff
   - Checks Python code formatting
   - Runs type checking with mypy

2. **Python tests**:
   - Runs tests for backend and core-py

3. **Python build**:
   - Builds all Python packages (backend, core-py, CLI)

4. **TypeScript lint and type check**:
   - Lints TypeScript/JavaScript code with ESLint
   - Runs TypeScript type checking

5. **TypeScript build**:
   - Builds all TypeScript projects (web-dashboard, vscode extension, github-app)

6. **TypeScript tests**:
   - Runs all TypeScript tests

### CI Workflow Triggers

The CI workflow (`.github/workflows/ci.yml`) runs automatically on:

- **All branch pushes**: Enables testing before creating a PR
- **Pull requests**: Runs when PRs are opened or updated
- **New commits on PR branches**: Automatically runs when you push to a branch with an open PR

### Running CI Checks Locally

Before committing, run the CI check script to ensure your code will pass CI:

```bash
just ci-check
```

This runs the same checks as GitHub Actions CI locally. See [CI Checks Before Committing](#ci-checks-before-committing) for more details.

### Other CI Workflows

1. **Pre-commit CI** (`pre-commit.yml`):
   - Runs all pre-commit hooks to ensure code quality
   - Runs on pull requests and pushes to main/develop

## Best Practices

1. **Run CI checks before committing**: Use `just ci-check` to run the same checks as GitHub Actions CI locally
2. **Always run pre-commit hooks before committing**: The hooks will catch most issues automatically
3. **Fix linting issues locally**: Don't rely on CI to catch formatting issues
4. **Run tests before pushing**: Ensure all tests pass locally
5. **Keep dependencies up to date**: Regularly update Python and Node.js dependencies
6. **Follow the code style**: The linters and formatters enforce consistent code style

## Troubleshooting

### Pre-commit hooks not running

If pre-commit hooks aren't running:

```bash
# Reinstall the hooks
uv run pre-commit uninstall
uv run pre-commit install
```

### Ruff or mypy errors

If you see errors from ruff or mypy that you believe are false positives:

1. Check the configuration in `pyproject.toml`
2. You can add specific ignores in the tool configuration
3. For mypy, you can use `# type: ignore` comments for specific lines

### ESLint or Prettier errors

If you see errors from ESLint or Prettier:

1. Run `npm run lint:fix` to auto-fix ESLint issues
2. Run `npm run format` to auto-fix Prettier issues
3. Check `.eslintrc.json` and `.prettierrc.json` for configuration
