# CLAUDE.md - AI Assistant Guide for Aura

This document provides essential context for AI assistants working with the Aura codebase.

## Project Overview

**Aura** is an AI-powered code review and education platform built as a polyglot monorepo. It provides struggle detection, code audit workflows, and educational lessons integrated across multiple platforms (CLI, VSCode extension, web dashboard, GitHub app).

## Repository Structure

```
aura/
├── apps/                    # Deployable applications
│   ├── backend/            # FastAPI Python API (port 8000)
│   └── web-dashboard/      # Next.js React dashboard (port 3000)
├── clients/                # Client applications
│   ├── cli/               # Python CLI tool (aura command)
│   ├── vscode/            # VSCode extension
│   └── github-app/        # Probot GitHub application
├── libs/                   # Shared libraries
│   ├── agentic-py/        # AI workflows, RAG pipeline, agents
│   └── shared-ts/         # Shared TypeScript types
├── docker/                 # Docker configuration
│   └── docker-compose.dev.yml
├── docs/                   # Documentation
│   └── lessons/           # Educational content (Java, Python, TypeScript)
├── deployment/             # Deployment artifacts
│   └── migration/         # Flyway database migrations
└── scripts/               # Automation scripts
```

## Technology Stack

### Backend (Python)

- **Framework**: FastAPI with uvicorn
- **Python Version**: 3.13
- **Database**: PostgreSQL 15 with pgvector extension
- **ORM**: SQLModel (SQLAlchemy wrapper)
- **Async Driver**: asyncpg
- **Caching**: Redis
- **AI/ML**: LangChain, LangGraph for workflow orchestration
- **Package Manager**: uv

### Frontend (TypeScript)

- **Framework**: Next.js 16 with React 19
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Form Handling**: react-hook-form with Zod validation
- **Testing**: Vitest (unit), Playwright (e2e)

## Backend Architecture

The backend follows a **layered architecture** pattern:

```
API Layer (FastAPI sub-applications)
    ↓
Service Layer (Business logic & orchestration)
    ↓
DAO Layer (Database abstraction)
    ↓
Database Layer (SQLModel ORM)
    ↓
Core Layer (Config, security, logging, exceptions)
```

### Key Directories (apps/backend/src/)

- `core/` - Configuration, exceptions, logging, security, metrics
- `db/` - Database models and session management
- `dao/` - Data Access Objects with CRUD operations
- `services/` - Business logic (auth, workflows, events, audit, redis)
- `api/v1/` - API endpoints organized as sub-applications

### API Sub-applications

Each module in `api/v1/` is self-contained with:

- `endpoints.py` - Route handlers
- `schemas.py` - Pydantic request/response models
- `exceptions.py` - Module-specific exceptions
- `router.py` - FastAPI router configuration

## Essential Commands

### Development

```bash
just dev              # Start all services (backend, web, postgres, redis)
just dev-detached     # Start in background
just dev-stop         # Stop all services
just dev-clean        # Stop and remove volumes
just dev-logs         # View logs from all services
```

### Testing

```bash
just test             # Run all tests (Python + TypeScript) in Docker
just test-py          # Run Python tests in Docker
just test-ts          # Run TypeScript tests in Docker
just test-local       # Run unit tests locally (excludes integration/e2e)
just test-py-integration-docker  # Run integration tests against Docker DB
```

### Code Quality

```bash
just lint             # Run all linters
just lint-fix         # Auto-fix linting issues
just pre-commit-all   # Run pre-commit hooks on all files
just ci-check         # Run CI checks locally (same as GitHub Actions)
just ci-check-fast    # CI checks without tests (faster)
just security-check   # Run bandit and npm audit
```

### Git & PR Workflow

```bash
just branch-create <name>     # Create feature branch from main
just branch-linear <id> <desc>  # Create branch with Linear integration
just pr-create <title> <desc>   # Create pull request
```

## Code Quality Standards

### Python

- **Linter**: Ruff (formatting + linting)
- **Type Checker**: MyPy
- **Security**: Bandit
- **Style**: Black-compatible formatting, 100 char line length

### TypeScript

- **Linter**: ESLint
- **Formatter**: Prettier
- **Type Checking**: TypeScript strict mode

### Pre-commit Hooks

All commits must pass pre-commit hooks:

- trailing-whitespace, end-of-file-fixer
- check-yaml, check-json, check-toml
- ruff (lint + format)
- mypy (type checking)
- prettier (TS/JS formatting)
- eslint
- bandit (security)
- hadolint (Dockerfile linting)

## Testing Patterns

### Python Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Isolated tests with mocked dependencies
- `@pytest.mark.integration` - Require database/Redis
- `@pytest.mark.e2e` - Full stack tests
- `@pytest.mark.performance` - Benchmarks

### Test Directory Structure

```
apps/backend/tests/
├── unit/              # Unit tests
│   └── auth/
├── integration/       # Integration tests
│   ├── auth/
│   ├── workflows/
│   └── rag/
├── e2e/              # End-to-end tests
└── performance/      # Performance tests
```

### Frontend Testing

- Unit tests: Vitest with @testing-library/react
- E2E tests: Playwright
- API mocking: MSW (Mock Service Worker)

## Environment Configuration

Configuration is managed via environment files:

- `.env.local` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Key environment variables:

- `ENVIRONMENT` - local/staging/production
- `POSTGRES_DB_URI` - Database connection string
- `REDIS_URL` - Redis connection
- `OPENAI_API_KEY` - For LLM features
- `LLM_ENABLED` - Enable/disable LLM features
- `RAG_ENABLED` - Enable/disable RAG service

See `.env.example` for complete list with documentation.

## CI/CD Workflows

GitHub Actions workflows in `.github/workflows/`:

| Workflow                 | Purpose                                   |
| ------------------------ | ----------------------------------------- |
| python-ci.yml            | Python lint, type check, tests            |
| typescript-ci.yml        | TypeScript lint, type check, build, tests |
| docker-build.yml         | Build and push Docker images              |
| vscode-extension-ci.yml  | VSCode extension build and test           |
| github-app-ci.yml        | GitHub app tests                          |
| web-dashboard-vercel.yml | Vercel deployment                         |

## Critical Rules for AI Assistants

### Before Committing

1. **ALWAYS run `just ci-check` before committing**
2. **NEVER commit if pre-commit hooks fail**
3. Fix all linting and type errors first
4. Ensure tests pass

### Code Style

- Follow SOLID principles
- Write self-documenting code with meaningful names
- Use type hints in Python (type checking is enabled)
- Use TypeScript strict mode
- Include comprehensive error handling

### Architecture Rules

- Apps should depend on libs, NOT on each other
- Keep shared code in `libs/`
- Follow the layered architecture in backend
- Each API module should be self-contained

### Security

- Never commit secrets or API keys
- Validate all inputs
- Use proper authentication/authorization
- Follow OWASP best practices
- Security checks run in pre-commit

### Testing

- Write unit tests for business logic
- Include integration tests for APIs
- Test error cases and edge conditions
- Unit tests must not require external services

## Common Development Tasks

### Adding a New API Endpoint

1. Create schemas in `api/v1/<module>/schemas.py`
2. Add service logic in `services/<module>/`
3. Implement endpoint in `api/v1/<module>/endpoints.py`
4. Add tests in `tests/unit/` and `tests/integration/`

### Adding Database Models

1. Define model in `db/models/`
2. Create DAO in `dao/`
3. Add Flyway migration in `deployment/migration/`

### Working with LangGraph Workflows

- Workflows are in `libs/agentic-py/workflows/`
- State definitions in `libs/agentic-py/states/`
- Agents in `libs/agentic-py/agents/`

## Useful Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture
- [Development Guide](docs/DEVELOPMENT.md) - Setup and workflow
- [User Guide](docs/USER_GUIDE.md) - API and feature usage
- [RAG Pipeline](docs/RAG.md) - RAG documentation
- [Security Guide](docs/SECURITY.md) - Security features

## Monorepo Dependencies

### Python Workspaces (uv)

```
apps/backend       → depends on libs/agentic-py
clients/cli        → depends on libs/agentic-py
libs/agentic-py    → standalone
```

### TypeScript Workspaces (npm)

```
apps/web-dashboard → depends on libs/shared-ts
clients/vscode     → depends on libs/shared-ts
clients/github-app → standalone
```

## Quick Reference

| Task                  | Command                     |
| --------------------- | --------------------------- |
| Start dev environment | `just dev`                  |
| Run all tests         | `just test`                 |
| Lint code             | `just lint`                 |
| Fix lint issues       | `just lint-fix`             |
| Run CI checks locally | `just ci-check`             |
| Create feature branch | `just branch-create <name>` |
| View Docker logs      | `just dev-logs`             |
| Backend only          | Port 8000                   |
| Frontend only         | Port 3000                   |
| PostgreSQL            | Port 5432                   |
