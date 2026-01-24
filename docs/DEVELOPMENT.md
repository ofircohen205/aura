# Development Guide

This document describes how to set up and work with the development environment for the Aura project.

> **Note**: This project uses **Docker-only development**. You don't need to install Python, Node.js, uv, or npm locally. Everything runs in Docker containers.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Docker-Based Development](#docker-based-development)
3. [Code Quality Tools](#code-quality-tools)
4. [Pre-commit Hooks](#pre-commit-hooks)
5. [Running Tests](#running-tests)
6. [Common Development Tasks](#common-development-tasks)
7. [CI/CD](#cicd)
8. [Development Workflow](#development-workflow)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: >= 20.10 (Required)
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: >= 2.0 (Required)
  - Usually included with Docker Desktop
- **Just**: (Optional, but recommended for convenient commands)
  - [Install Just](https://github.com/casey/just#installation)

### Installation

No installation needed! Everything runs in Docker.

### First Time Setup

On first run, Docker will:

1. Build container images
2. Install Python dependencies (via uv)
3. Install Node.js dependencies (via npm)
4. Run database migrations
5. Start all services

This may take a few minutes. Subsequent starts are much faster.

### Configuration

The backend uses environment-based configuration. Create a `.env.local` file in the project root for local development:

```bash
# Environment
ENVIRONMENT=local

# Database Configuration
# NOTE: These are example credentials for local development only
# In production, use strong, unique credentials
POSTGRES_DB_URI=postgresql+psycopg://aura:aura@localhost:5432/aura_db
POSTGRES_POOL_MAX_SIZE=20
POSTGRES_POOL_MIN_SIZE=5

# CORS Configuration
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# API Configuration
API_TITLE=Aura Backend
API_VERSION=0.1.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=text

# Web Dashboard Configuration
# Required: API URL for the frontend to connect to the backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, use `.env.production` or set environment variables directly. The configuration system supports:

- `.env.local` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Set the `ENVIRONMENT` variable to select which config file to use.

### Project Structure

- `apps/`
  - `backend`: Python FastAPI application
  - `web-dashboard`: Next.js web application
- `clients/`
  - `cli`: Python command-line interface
  - `vscode`: TypeScript VSCode extension
- `libs/`
  - `agentic-py`: Shared Python business logic

## Quick Start

### Start Development Environment

```bash
# Start all services (backend, web, postgres, etc.)
just dev

# Or in detached mode
just dev-detached
```

This will start:

- **Backend API** on `http://localhost:8000`
- **Web Dashboard** on `http://localhost:3000`
- **PostgreSQL** on `localhost:5432` (default credentials for local dev only)
- **Redis** on `localhost:6379` (for caching and rate limiting)
- **Dev Tools Container** for running commands

**Note**: The database initialization scripts automatically create both `aura_db` (main database) and `aura` (default database matching username) to prevent connection errors.

### Access Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)
- **Web Dashboard**: http://localhost:3000
- **Database**: `localhost:5432` (default credentials for local dev only)

### Running Commands

All development commands run inside Docker containers:

```bash
# Run tests
just test

# Lint code
just lint

# Get shell in dev container
just docker-shell

# Run any command
just docker-exec "your command here"
```

### Editing Code

Edit files on your **host machine** using your preferred editor. Changes are automatically reflected in containers via volume mounts. Hot reload is enabled for both backend and web dashboard.

### CLI Usage

To use the CLI, run commands in the dev-tools container:

```bash
# Get shell
just docker-shell

# Then run CLI commands
cd clients/cli
uv run aura --help
```

### VSCode Extension

The VSCode extension development still happens on your host machine:

1. Navigate to `clients/vscode`
2. Run `npm install` (or use Docker: `just docker-exec "cd clients/vscode && npm install"`)
3. Open in VSCode and press `F5` to launch Extension Development Host

### Stop Services

```bash
# Stop all services
just dev-stop

# Stop and remove volumes (clean slate)
just dev-clean
```

## Docker-Based Development

All development tasks (coding, testing, linting) are performed inside Docker containers.

### Running Commands in Docker

All development commands run inside the `dev-tools` container:

```bash
# Get a shell in the dev-tools container
just docker-shell

# Or execute a single command
just docker-exec "command here"
```

### Container Structure

**Services:**

1. **backend** - FastAPI backend service (Port: 8000, Hot reload enabled)
2. **web-dashboard** - Next.js web application (Port: 3000, Hot reload enabled)
3. **postgres** - PostgreSQL database (Port: 5432, Persistent data volume)
4. **redis** - Redis cache service (Port: 6379, for authentication tokens and rate limiting)
5. **flyway** - Database migrations (Runs on startup)
6. **db-init** - Database initialization (Ensures databases exist)
7. **dev-tools** - Development tools container (Contains all dev tools)

**Volumes:**

- `postgres_data` - PostgreSQL data persistence
- `redis_data` - Redis data persistence (for cache and rate limiting)
- `backend-venv` - Python virtual environment (shared)
- Anonymous volumes for `node_modules` - Node.js dependencies (isolated per container, prevents host directory conflicts)

### File Editing

Edit files on your **host machine** using your preferred editor. Changes are automatically reflected in containers via volume mounts:

- `apps/backend/` → `/app/apps/backend` in containers
- `libs/agentic-py/` → `/app/libs/agentic-py` in containers
- `apps/web-dashboard/` → `/app/apps/web-dashboard` in containers

Hot reload is enabled for both backend and web dashboard.

## Development Workflow

For the complete development pipeline including Linear integration, see [Development Workflow](#development-workflow) below.

### Common Development Tasks

#### View Logs

```bash
# View all logs
just dev-logs

# View specific service logs
just dev-logs-service backend
just dev-logs-service web-dashboard
just dev-logs-service postgres
```

#### Database Access

```bash
# Connect to PostgreSQL from host
psql -h localhost -U aura -d aura_db

# Or from inside container
just docker-exec "psql -h postgres -U aura -d aura_db"
```

#### Rebuild Containers

```bash
# Rebuild all containers
docker-compose -f docker/docker-compose.dev.yml build

# Rebuild specific service
docker-compose -f docker/docker-compose.dev.yml build backend
```

## Code Quality Tools

### Python

The project uses the following tools for Python code quality:

- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **Bandit**: Security linter

#### Running Python Linters (in Docker)

```bash
# Run all Python linting
just lint-py

# Run ruff linting
just docker-exec "uv run ruff check apps/backend libs/agentic-py clients/cli"

# Auto-fix linting issues
just docker-exec "uv run ruff check --fix apps/backend libs/agentic-py clients/cli"

# Run ruff formatting
just docker-exec "uv run ruff format apps/backend libs/agentic-py clients/cli"

# Run mypy type checking
just docker-exec "uv run mypy apps/backend libs/agentic-py clients/cli"
```

### TypeScript/JavaScript

The project uses the following tools for TypeScript/JavaScript code quality:

- **ESLint**: JavaScript and TypeScript linter
- **Prettier**: Code formatter

#### Running TypeScript/JavaScript Linters (in Docker)

```bash
# Run all TypeScript linting
just lint-ts

# Run ESLint
just docker-exec "npm run lint"

# Auto-fix ESLint issues
just docker-exec "npm run lint:fix"

# Format code with Prettier
just docker-exec "npm run format"

# Run TypeScript type checking
just docker-exec "npm run type-check"
```

### Running All Linters

```bash
# Run all linters
just lint

# Auto-fix linting issues
just lint-fix
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
just docker-exec "uv run pre-commit run --all-files"
```

Or on specific files:

```bash
just docker-exec "uv run pre-commit run --files path/to/file.py"
```

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
uv run ruff check apps/backend libs/agentic-py clients/cli

# Auto-fix linting issues
uv run ruff check --fix apps/backend libs/agentic-py clients/cli

# Run ruff formatting
uv run ruff format apps/backend libs/agentic-py clients/cli

# Check formatting without making changes
uv run ruff format --check apps/backend libs/agentic-py clients/cli

# Run mypy type checking
uv run mypy apps/backend libs/agentic-py clients/cli
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
2. **Python tests**: backend and agentic-py tests
3. **Python build**: Builds all Python packages
4. **TypeScript lint and type check**: ESLint and TypeScript type checking
5. **TypeScript build**: Builds all TypeScript projects
6. **TypeScript tests**: Runs all TypeScript tests

**Note**: The CI workflow (`.github/workflows/ci.yml`) runs automatically on all branch pushes and pull requests, so running this script before committing helps catch issues early.

## Running Tests

### Python Tests (in Docker)

```bash
# Run all tests
just test

# Run Python tests only
just test-py

# Run specific test file
just docker-exec "cd apps/backend && uv run pytest tests/test_specific.py -v"
```

### TypeScript/JavaScript Tests (in Docker)

```bash
# Run all tests
just test

# Run TypeScript tests only
just test-ts

# Run specific test file
just docker-exec "cd apps/web-dashboard && npm test ExampleCard.test.tsx"
```

### Web Dashboard Testing

The web dashboard uses Vitest for unit/integration tests and Playwright for E2E tests.

**Test Structure:**

```
tests/
├── setup.ts              # Test setup and global mocks
├── utils/
│   └── test-utils.tsx    # Testing utilities and helpers
├── unit/                 # Unit tests
│   ├── components/       # Component tests
│   └── lib/             # Utility function tests
├── integration/          # Integration tests
│   └── api/             # API client tests
└── e2e/                  # End-to-end tests
    ├── auth.spec.ts     # Authentication flow tests
    └── dashboard.spec.ts # Dashboard navigation tests
```

**Running Tests:**

```bash
# Unit and integration tests (Vitest)
npm test
npm test -- --watch
npm run test:ui
npm run test:coverage

# E2E tests (Playwright)
npm run test:e2e
npm run test:e2e -- --ui
npm run test:e2e -- --headed
```

**Test Coverage Goals:**

- Unit Tests: 80%+ coverage for components and utilities
- Integration Tests: All API clients should have tests
- E2E Tests: Critical user flows (auth, navigation, core features)

**Best Practices:**

1. Test user behavior, not implementation details
2. Use semantic queries (getByRole, getByLabelText)
3. Mock external dependencies (API calls, router)
4. Keep tests isolated (cleanup between tests)
5. Write descriptive test names
6. Test error cases and edge cases

## Common Development Tasks

### Creating a New Feature

#### Backend: Adding a New API Endpoint

The backend follows a layered architecture. You must add files in the specific order of dependencies: **Model → DAO → Service → API**.

1. **Define Database Model** (`src/db/models/example.py`)

   Create the SQLAlchemy/SQLModel definition:

   ```python
   from sqlmodel import Field, SQLModel
   from uuid import UUID, uuid4
   from datetime import datetime

   class Example(SQLModel, table=True):
       id: UUID = Field(default_factory=uuid4, primary_key=True)
       name: str
       description: str
       created_at: datetime = Field(default_factory=datetime.now)
   ```

2. **Create DAO** (`src/dao/example.py`)

   Inherit from `BaseDAO` to get standard CRUD operations automatically:

   ```python
   from src.dao.base import BaseDAO
   from src.db.models.example import Example

   class ExampleDAO(BaseDAO[Example, ExampleCreate, ExampleUpdate]):
       pass

   example_dao = ExampleDAO(Example)
   ```

3. **Create Service & Business Exceptions** (`src/services/example/`)

   Define exceptions and implement service logic. See [Architecture Guide](ARCHITECTURE.md) for detailed examples.

4. **Create API Layer** (`src/api/v1/example/`)

   Create schemas, exception handlers, and endpoints. Each API module uses a FastAPI sub-application pattern.

5. **Register Sub-Application** (`src/main.py`)

   Mount the sub-application in the main FastAPI app.

#### Frontend: Adding a New Feature

The frontend uses a **Screaming Architecture**. All logic related to a feature stays within `src/features/`.

1. Create feature structure: `src/features/example/` with subfolders (components, hooks, pages, services, stores, types)
2. Create types, services, components, pages
3. Export feature via `index.ts`
4. Add route in router

For detailed code examples, see the [Architecture Guide](ARCHITECTURE.md) and examples above.

### Database Migrations

Use the migration scripts located in the deployment folder to manage schema changes.

```bash
# Location: deployment/migration

# Naming Convention: V{version}__{description}.sql

# 1. Create a new SQL file
touch deployment/migration/V21__add_example_table.sql

# 2. Add SQL content
# 3. Migrations run automatically on Docker Compose startup
```

### Debugging

#### Backend Debugging (FastAPI)

```bash
# 1. Run with Debugger
# Ensure your IDE (VS Code/PyCharm) is attached to port 5678
just docker-exec "cd apps/backend && uv run python -m debugpy --listen 0.0.0.0:5678 src/main.py"

# 2. Check Application Logs
just dev-logs-service backend

# 3. Direct Database Access
just docker-exec "psql -h postgres -U aura -d aura_db"
```

#### Frontend Debugging (React 19)

1. **React DevTools**: Use the "Components" tab to inspect the component tree
2. **TanStack Query DevTools**: Click the floating flower icon in development
3. **Network Tab**: Filter by `Fetch/XHR` to inspect API calls

## CI/CD

The project uses GitHub Actions for continuous integration. The main CI pipeline (`ci.yml`) runs:

1. **Python lint and type check**:
   - Lints Python code with ruff
   - Checks Python code formatting
   - Runs type checking with mypy

2. **Python tests**:
   - Runs tests for backend and agentic-py

3. **Python build**:
   - Builds all Python packages (backend, agentic-py, CLI)

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

1. **Always use Docker commands** - Don't install dependencies on host
2. **Edit files on host** - Use your preferred editor
3. **Run commands in Docker** - Use `just docker-exec` or `just docker-shell`
4. **Keep containers running** - Start once, work all day
5. **Use volumes** - Don't copy files into containers
6. **Check logs** - Use `just dev-logs` when debugging
7. **Run CI checks before committing**: Use `just ci-check` to run the same checks as GitHub Actions CI locally
8. **Always run pre-commit hooks before committing**: The hooks will catch most issues automatically
9. **Fix linting issues locally**: Don't rely on CI to catch formatting issues
10. **Run tests before pushing**: Ensure all tests pass locally
11. **Follow the code style**: The linters and formatters enforce consistent code style

## Troubleshooting

### Containers Won't Start

```bash
# Check logs
just dev-logs

# Rebuild containers
docker-compose -f docker/docker-compose.dev.yml build --no-cache

# Clean and restart
just dev-clean
just dev
```

### Web Dashboard Environment Variable Error

If you see an error about missing `NEXT_PUBLIC_API_URL`:

```bash
# The environment variable is set in docker-compose.dev.yml
# Restart the web-dashboard container to pick it up:
docker-compose -f docker/docker-compose.dev.yml restart web-dashboard

# Or rebuild if needed:
docker-compose -f docker/docker-compose.dev.yml up -d --build web-dashboard
```

The default value is `http://localhost:8000` which points to the backend API. You can override it by setting the `NEXT_PUBLIC_API_URL` environment variable in your shell before running docker-compose.

### Tests Failing

```bash
# Check if services are running
docker-compose -f docker/docker-compose.dev.yml ps

# Ensure postgres is healthy
docker-compose -f docker/docker-compose.dev.yml exec postgres pg_isready -U aura

# Run tests with verbose output
just docker-exec "cd apps/backend && uv run pytest tests/ -vv"
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Web
lsof -i :5432  # Postgres

# Stop conflicting services or change ports in docker-compose.dev.yml
```

### Pre-commit hooks not running

If pre-commit hooks aren't running:

```bash
# Reinstall the hooks
just docker-exec "uv run pre-commit uninstall"
just docker-exec "uv run pre-commit install"
```

### Ruff or mypy errors

If you see errors from ruff or mypy that you believe are false positives:

1. Check the configuration in `pyproject.toml`
2. You can add specific ignores in the tool configuration
3. For mypy, you can use `# type: ignore` comments for specific lines

### ESLint or Prettier errors

If you see errors from ESLint or Prettier:

1. Run `just lint-fix` to auto-fix issues
2. Check `.eslintrc.json` and `.prettierrc.json` for configuration

## Development Workflow

The development pipeline follows these stages:

1. **Read Task/Story** - Understand requirements from Linear
2. **Plan Sub-tasks** - Break down into implementable pieces
3. **Create Branch** - Create feature branch from main
4. **Implement** - Each sub-task owned by dedicated role
5. **Write Tests** - Ensure code quality
6. **Code Review** - Review using appropriate roles
7. **Fix Issues** - Address review feedback
8. **Commit & Push** - Commit with proper conventions
9. **Create PR** - Open pull request for review

For detailed workflow information, see [Linear Integration Guide](LINEAR.md).

## Related Documentation

- [Linear Integration](LINEAR.md) - Linear workflow and automation
- [Architecture Guide](ARCHITECTURE.md) - System architecture overview
- [Deployment Guide](DEPLOYMENT.md) - Deployment procedures
