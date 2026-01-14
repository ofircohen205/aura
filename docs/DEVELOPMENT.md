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

The project uses GitHub Actions for continuous integration. The CI pipeline:

1. **Python CI** (`python-ci.yml`):
   - Lints Python code with ruff
   - Checks Python code formatting
   - Runs type checking with mypy
   - Runs tests for backend and core-py
   - Builds Python packages

2. **TypeScript CI** (`typescript-ci.yml`):
   - Lints TypeScript/JavaScript code with ESLint
   - Runs TypeScript type checking
   - Builds all TypeScript projects
   - Runs tests

3. **Pre-commit CI** (`pre-commit.yml`):
   - Runs all pre-commit hooks to ensure code quality

All workflows run automatically on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Best Practices

1. **Always run pre-commit hooks before committing**: The hooks will catch most issues automatically
2. **Fix linting issues locally**: Don't rely on CI to catch formatting issues
3. **Run tests before pushing**: Ensure all tests pass locally
4. **Keep dependencies up to date**: Regularly update Python and Node.js dependencies
5. **Follow the code style**: The linters and formatters enforce consistent code style

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
