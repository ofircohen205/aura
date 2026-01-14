# Aura Monorepo

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

See [docs/workflows/project-architecture.md](docs/workflows/project-architecture.md) for detailed architecture documentation.

## Setup

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python)
- [Node.js](https://nodejs.org/) & npm (for TypeScript)
- [Just](https://github.com/casey/just) (optional, for command running)

### Installation

```bash
# Install all dependencies
just install

# Or manually:
uv sync
npm install
```

## Development

```bash
# Run backend
just dev-backend

# Run web dashboard
just dev-web
```
