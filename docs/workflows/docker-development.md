# Docker-Only Development Guide

This guide explains how to develop Aura entirely within Docker containers. All development tasks (coding, testing, linting) are performed inside Docker containers.

## Prerequisites

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Just** (optional): For convenient command execution

## Quick Start

### 1. Start Development Environment

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
- **Dev Tools Container** for running commands

### 2. Access Services

- **Backend API**: http://localhost:8000
- **Web Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### 3. Stop Services

```bash
# Stop all services
just dev-stop

# Stop and remove volumes (clean slate)
just dev-clean
```

## Development Workflow

### Running Commands in Docker

All development commands run inside the `dev-tools` container:

```bash
# Get a shell in the dev-tools container
just docker-shell

# Or execute a single command
just docker-exec "command here"
```

### Testing

```bash
# Run all tests
just test

# Run Python tests only
just test-py

# Run TypeScript tests only
just test-ts
```

### Linting

```bash
# Run all linters
just lint

# Run Python linting
just lint-py

# Run TypeScript linting
just lint-ts

# Auto-fix linting issues
just lint-fix
```

### Code Quality

```bash
# Run code review checks
just code-review

# Run security checks
just security-check

# Run pre-commit hooks
just pre-commit-all
```

## Container Structure

### Services

1. **backend** - FastAPI backend service
   - Port: 8000
   - Hot reload enabled
   - Volume mounts for live code changes

2. **web-dashboard** - Next.js web application
   - Port: 3000
   - Hot reload enabled
   - Volume mounts for live code changes

3. **postgres** - PostgreSQL database
   - Port: 5432
   - Persistent data volume
   - Health checks enabled

4. **flyway** - Database migrations
   - Runs migrations on startup
   - Waits for postgres to be healthy

5. **dev-tools** - Development tools container
   - Contains all development tools (uv, npm, just, etc.)
   - Used for running tests, linting, etc.
   - Volume mounts entire codebase

### Volumes

- `postgres_data` - PostgreSQL data persistence
- `backend-venv` - Python virtual environment (shared)
- `web-node-modules` - Node.js dependencies (shared)

## Development Pipeline in Docker

### 1. Read Task/Story

Same as before - read from Linear or GitHub.

### 2. Plan Sub-tasks

Plan as usual, but remember all work happens in Docker.

### 3. Create Branch

```bash
# Create branch (runs on host, but that's fine)
just branch-create feature/OFI-123-description
```

### 4. Implement

Edit files on your host machine. Changes are automatically reflected in containers via volume mounts.

- **Backend**: Edit files in `apps/backend/` - changes reload automatically
- **Web**: Edit files in `apps/web-dashboard/` - changes reload automatically

### 5. Write Tests

```bash
# Run tests in Docker
just test
```

### 6. Code Review

```bash
# Run code review checks in Docker
just code-review
```

### 7. Fix Issues

Edit files, then re-run checks:

```bash
just lint-fix
just test
```

### 8. Commit & Push

```bash
# Commit (runs on host)
just commit "feat(api): add endpoint [OFI-123]"

# Push (runs on host)
just push
```

### 9. Create PR

```bash
# Create PR (runs on host)
just pr-create "Title" "Description"
```

## Common Tasks

### View Logs

```bash
# View all logs
just dev-logs

# View specific service logs
just dev-logs-service backend
just dev-logs-service web-dashboard
just dev-logs-service postgres
```

### Database Access

```bash
# Connect to PostgreSQL from host
psql -h localhost -U aura -d aura_db

# Or from inside container
just docker-exec "psql -h postgres -U aura -d aura_db"
```

### Run Custom Commands

```bash
# Run any command in dev-tools container
just docker-exec "cd apps/backend && uv run python -m pytest tests/test_specific.py"

# Or get a shell
just docker-shell
```

### Rebuild Containers

```bash
# Rebuild all containers
docker-compose -f docker/docker-compose.dev.yml build

# Rebuild specific service
docker-compose -f docker/docker-compose.dev.yml build backend
```

## File Editing

Edit files on your **host machine** using your preferred editor. Changes are automatically reflected in containers via volume mounts:

- `apps/backend/` → `/app/apps/backend` in containers
- `libs/core-py/` → `/app/libs/core-py` in containers
- `apps/web-dashboard/` → `/app/apps/web-dashboard` in containers

## Environment Variables

Environment variables are set in `docker-compose.dev.yml`. To override:

1. Create `.env` file in project root
2. Add variables (they'll be automatically loaded)
3. Restart services: `just dev-stop && just dev`

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

### Volume Permission Issues

```bash
# Fix permissions (if needed)
docker-compose -f docker/docker-compose.dev.yml exec dev-tools chown -R $(id -u):$(id -g) /app
```

### Dependencies Not Updating

```bash
# Rebuild containers to pick up dependency changes
docker-compose -f docker/docker-compose.dev.yml build --no-cache

# Or rebuild specific service
docker-compose -f docker/docker-compose.dev.yml build dev-tools
```

## Best Practices

1. **Always use Docker commands** - Don't install dependencies on host
2. **Edit files on host** - Use your preferred editor
3. **Run commands in Docker** - Use `just docker-exec` or `just docker-shell`
4. **Keep containers running** - Start once, work all day
5. **Use volumes** - Don't copy files into containers
6. **Check logs** - Use `just dev-logs` when debugging

## Advantages of Docker-Only Development

1. **Consistent Environment** - Same setup for all developers
2. **No Local Dependencies** - No need to install Python, Node, etc.
3. **Isolated** - Doesn't pollute your system
4. **Reproducible** - Easy to share exact environment
5. **Production-like** - Closer to production environment

## Migration from Local Development

If you were developing locally before:

1. **Stop local services** - Stop any local Python/Node processes
2. **Start Docker** - Run `just dev`
3. **Update commands** - Use Docker commands (already in Justfile)
4. **Keep editing locally** - Your editor still works the same

## Next Steps

- Review `docs/workflows/development-pipeline.md` for full pipeline
- Check `docs/workflows/linear-integration.md` for Linear usage
- See `docs/GETTING_STARTED.md` for project overview
