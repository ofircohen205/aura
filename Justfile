# Justfile

# List available recipes
default:
    @just --list

# Install all dependencies (Python & Node)
install: install-py install-node

# Install Python dependencies
install-py:
    uv sync

# Install Node dependencies
install-node:
    npm install

# Run backend development server
dev-backend:
    cd apps/backend && uv run uvicorn main:app --reload

# Run web dashboard development server
dev-web:
    cd apps/web-dashboard && npm run dev

# Run docker compose dev
docker-dev:
    docker-compose -f docker/docker-compose.dev.yml up --build
