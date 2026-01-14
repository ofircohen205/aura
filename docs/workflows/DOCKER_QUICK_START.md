# Docker Quick Start

Get up and running with Aura in 3 steps.

## 1. Start Development Environment

```bash
just dev
```

This starts:

- Backend API on `http://localhost:8000`
- Web Dashboard on `http://localhost:3000`
- PostgreSQL database
- Development tools container

## 2. Run Tests

```bash
just test
```

All tests run inside Docker containers.

## 3. Start Developing

Edit files on your host machine. Changes automatically reload in containers.

## Common Commands

```bash
# Start services
just dev

# Run tests
just test

# Lint code
just lint

# Get shell in dev container
just docker-shell

# View logs
just dev-logs

# Stop services
just dev-stop
```

## Full Documentation

- **Docker Development**: `docs/workflows/docker-development.md`
- **Development Pipeline**: `docs/workflows/development-pipeline.md`
- **Getting Started**: `docs/GETTING_STARTED.md`
