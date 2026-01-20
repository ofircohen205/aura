# Aura Monorepo

[![Python CI](https://github.com/ofircohen205/aura/actions/workflows/python-ci.yml/badge.svg)](https://github.com/ofircohen205/aura/actions/workflows/python-ci.yml)
[![TypeScript CI](https://github.com/ofircohen205/aura/actions/workflows/typescript-ci.yml/badge.svg)](https://github.com/ofircohen205/aura/actions/workflows/typescript-ci.yml)
[![VSCode Extension](https://github.com/ofircohen205/aura/actions/workflows/vscode-extension-ci.yml/badge.svg)](https://github.com/ofircohen205/aura/actions/workflows/vscode-extension-ci.yml)
[![GitHub App](https://github.com/ofircohen205/aura/actions/workflows/github-app-ci.yml/badge.svg)](https://github.com/ofircohen205/aura/actions/workflows/github-app-ci.yml)
[![Docker Build](https://github.com/ofircohen205/aura/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ofircohen205/aura/actions/workflows/docker-build.yml)

Welcome to the **Aura** monorepo! This project follows a polyglot structure managing both Python and TypeScript components.

## Structure

- **apps/**: Deployable applications
  - `backend`: FastAPI orchestration layer (Python)
    - Follows layered architecture: Core → Database → Service → API
    - Uses SQLModel for database models
    - Service layer for business logic
    - Sub-application pattern for API organization
  - `web-dashboard`: Next.js dashboard (TypeScript)
- **clients/**: Frontend clients
  - `vscode`: VSCode Extension (TypeScript)
  - `cli`: Guardian CLI (Python)
  - `github-app`: Probot App (TypeScript)
- **libs/**: Shared libraries
  - `core-py`: Core business logic (Python)
    - LangGraph workflows (struggle detection, code audit)
    - Postgres checkpointer for workflow state
  - `shared-ts`: Shared types/schemas (TypeScript)
- **docker/**: Infrastructure configuration
  - Docker Compose for local development
  - Database migrations via Flyway

## Architecture Overview

The backend follows a **layered architecture** pattern:

1. **Core Layer** (`apps/backend/src/core/`): Configuration, exceptions, logging, security
2. **Database Layer** (`apps/backend/src/db/`): SQLModel models and async session management
3. **Service Layer** (`apps/backend/src/services/`): Business logic and workflow orchestration
4. **API Layer** (`apps/backend/src/api/v1/`): FastAPI sub-applications with endpoints, schemas, and exception handlers

Each API module (workflows, events, audit) is a self-contained sub-application with:

- Request/response schemas
- Service layer integration
- Exception handlers
- Proper error responses

See [Architecture Guide](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) >= 20.10 (Required)
- [Docker Compose](https://docs.docker.com/compose/) >= 2.0 (Required)
- [Just](https://github.com/casey/just) (Optional, for convenient commands)

### Quick Start

```bash
# Start all development services
just dev
```

This will start:

- Backend API on http://localhost:8000
- Web Dashboard on http://localhost:3000
- PostgreSQL database on localhost:5432

### Installation

No installation needed! Everything runs in Docker containers. See [Development Guide](docs/DEVELOPMENT.md) for detailed setup instructions.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive guide to using Aura (API, CLI, workflows)
- **[Development Guide](docs/DEVELOPMENT.md)** - Setup, development workflow, and practices
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System architecture overview
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deployment procedures, infrastructure, and CI/CD
- **[RAG Pipeline](docs/RAG.md)** - RAG pipeline documentation, chunking strategies, and model selection
- **[Linear Integration](docs/LINEAR.md)** - Project management and workflow
- **[Requirements](docs/REQUIREMENTS.md)** - Product and technical requirements
- **[Security Guide](docs/SECURITY.md)** - Security features and best practices

## Development

```bash
# Start all services
just dev

# Run backend only
just dev-backend

# Run web dashboard only
just dev-web

# Run tests
just test

# Lint code
just lint
```
