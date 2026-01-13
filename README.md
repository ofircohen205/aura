# Aura Monorepo

Welcome to the **Aura** monorepo! This project follows a polyglot structure managing both Python and TypeScript components.

## Structure

- **apps/**: Deployable applications
    - `backend`: FastAPI orchestration layer (Python)
    - `web-dashboard`: Next.js dashboard (TypeScript)
- **clients/**: Frontend clients
    - `vscode`: VSCode Extension (TypeScript)
    - `cli`: Guardian CLI (Python)
    - `github-app`: Probot App (TypeScript)
- **libs/**: Shared libraries
    - `core-py`: Core business logic (Python)
    - `shared-ts`: Shared types/schemas (TypeScript)
- **docker/**: Infrastructure configuration

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