# Justfile

# List available recipes
default:
    @just --list

# =============================================================================
# Installation & Setup
# =============================================================================

# Install all dependencies (Python & Node)
install: install-py install-node

# Install Python dependencies
install-py:
    uv sync

# Install Node dependencies
install-node:
    @bash -c 'source ~/.nvm/nvm.sh 2>/dev/null || true; nvm use 20 >/dev/null 2>&1 || true; npm install'

# =============================================================================
# Docker Development Environment
# =============================================================================

# Start all development services (backend, web, postgres, etc.)
dev:
    docker system prune -f; \
    docker image prune -f; \
    docker volume prune -f; \
    docker compose -f docker/docker-compose.dev.yml up --build

# Rebuild all development services
dev-rebuild:
    docker system prune -f; \
    docker image prune -f; \
    docker volume prune -f; \
    docker compose -f docker/docker-compose.dev.yml up -d --build --force-recreate

# Start development services in detached mode
dev-detached:
    docker system prune -f; \
    docker image prune -f; \
    docker volume prune -f; \
    docker compose -f docker/docker-compose.dev.yml up -d --build

# Stop all development services
dev-stop:
    docker system prune -f; \
    docker image prune -f; \
    docker volume prune -f; \
    docker compose -f docker/docker-compose.dev.yml down

# Stop and remove volumes (clean slate)
dev-clean:
    docker system prune -f; \
    docker image prune -f; \
    docker volume prune -f; \
    docker compose -f docker/docker-compose.dev.yml down -v

# View logs from all services
dev-logs:
    docker compose -f docker/docker-compose.dev.yml logs -f

# View logs from specific service
# Usage: just dev-logs-service backend
dev-logs-service SERVICE:
    docker compose -f docker/docker-compose.dev.yml logs -f {{SERVICE}}

# Execute command in dev-tools container
# Usage: just docker-exec "command"
docker-exec COMMAND:
    docker compose -f docker/docker-compose.dev.yml exec dev-tools {{COMMAND}}

# Get shell in dev-tools container
docker-shell:
    docker compose -f docker/docker-compose.dev.yml exec dev-tools /bin/bash

# =============================================================================
# Development Pipeline Commands
# =============================================================================

# Create a new feature branch from main
# Usage: just branch-create feature/LIN-123-description
branch-create BRANCH_NAME:
    @echo "Creating branch: {{BRANCH_NAME}}"
    git checkout main
    git pull origin main
    git checkout -b {{BRANCH_NAME}}
    @echo "✓ Branch {{BRANCH_NAME}} created and checked out"

# Create a branch linked to Linear issue
# Usage: just branch-linear AURA-123 "description"
branch-linear ISSUE_ID DESCRIPTION:
    @bash scripts/branch-with-linear.sh {{ISSUE_ID}} "{{DESCRIPTION}}"

# Run all tests (Python + TypeScript) in Docker
test:
    @echo "Running all tests in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/backend && uv run pytest tests/ -v"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd libs/core-py && uv run pytest tests/ -v" || echo "No tests in core-py"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm test"

# Run Python tests in Docker
test-py:
    @echo "Running Python tests in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/backend && uv run pytest tests/ -v"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd libs/core-py && uv run pytest tests/ -v" || echo "No tests in core-py"

# Run TypeScript tests in Docker
test-ts:
    @echo "Running TypeScript tests in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm test"

# Run linting (Python + TypeScript) in Docker
lint:
    @echo "Running linters in Docker..."
    just lint-py
    just lint-ts

# Run Python linting in Docker
lint-py:
    @echo "Linting Python code in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run ruff check apps/backend libs/core-py clients/cli"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run mypy apps/backend libs/core-py clients/cli"

# Run TypeScript linting in Docker
lint-ts:
    @echo "Linting TypeScript code in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm run lint"

# Auto-fix linting issues in Docker
lint-fix:
    @echo "Fixing linting issues in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run ruff check --fix apps/backend libs/core-py clients/cli"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run ruff format apps/backend libs/core-py clients/cli"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm run lint:fix"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm run format"

# Run pre-commit hooks on all files in Docker
pre-commit-all:
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run pre-commit run --all-files"

# Run CI checks locally (same as GitHub Actions CI)
# Usage: just ci-check [--skip-tests] [--skip-build]
ci-check:
    @bash scripts/ci-check.sh

# Run CI checks without tests (faster for quick validation)
ci-check-fast:
    @bash scripts/ci-check.sh --skip-tests --skip-build

# Run code quality checks (lint + test)
quality-check:
    @echo "Running quality checks..."
    just lint
    just test

# Create a pull request
# Usage: just pr-create "Title" "Description"
pr-create TITLE DESCRIPTION:
    gh pr create --title "{{TITLE}}" --body "{{DESCRIPTION}}"

# Create a pull request with Linear issue link
# Usage: just pr-linear "Title" "Description" AURA-123
pr-linear TITLE DESCRIPTION ISSUE_ID:
    @echo "Creating PR linked to Linear issue {{ISSUE_ID}}..."
    @BODY="## Description\n\n{{DESCRIPTION}}\n\n## Linear Issue\n\nCloses {{ISSUE_ID}}\n\nView in Linear: https://linear.app/ofircohen/issue/{{ISSUE_ID}}"; \
    gh pr create --title "{{TITLE}}" --body "$$BODY"
    @echo "✓ PR created and linked to {{ISSUE_ID}}"

# =============================================================================
# Linear Integration Commands
# =============================================================================

# View Linear issue
# Usage: just linear-view LIN-123
linear-view ISSUE_ID:
    @echo "Viewing Linear issue {{ISSUE_ID}}..."
    @echo "Use Linear MCP tools or Linear CLI to view issue"

# Create Linear issue
# Usage: just linear-create "Title" "Description" "Team"
linear-create TITLE DESCRIPTION TEAM:
    @echo "Creating Linear issue..."
    @echo "Title: {{TITLE}}"
    @echo "Description: {{DESCRIPTION}}"
    @echo "Team: {{TEAM}}"
    @echo "Use Linear MCP tools or Linear CLI to create issue"

# Create Linear issue from template
# Usage: just linear-template feature "Title" "Team" [priority] [assignee]
# Priority: Urgent, High, Normal, Low (default: Normal)
# Assignee: User email, name, or 'me' (optional)
linear-template TEMPLATE TITLE TEAM PRIORITY='Normal' ASSIGNEE='':
    @bash scripts/create-linear-issue.sh {{TEMPLATE}} "{{TITLE}}" {{TEAM}} aura {{PRIORITY}} {{ASSIGNEE}}

# =============================================================================
# Code Review
# =============================================================================

# Run code review checks
code-review:
    @echo "Running code review checks..."
    just lint
    just test
    @echo "✓ Code review checks complete"
    @echo "Review CODE_REVIEW.md for detailed guidelines"

# =============================================================================
# Security
# =============================================================================

# Run security checks in Docker
security-check:
    @echo "Running security checks in Docker..."
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "uv run bandit -r apps/backend libs/core-py clients/cli"
    docker compose -f docker/docker-compose.dev.yml exec -T dev-tools bash -c "cd apps/web-dashboard && npm audit"

# =============================================================================
# Git Helpers
# =============================================================================

# Show current branch
branch:
    @git branch --show-current

# Show git status
status:
    @git status

# Show uncommitted changes
diff:
    @git diff

# Commit changes with message
# Usage: just commit "feat(api): add endpoint [LIN-123]"
commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"

# Push current branch
push:
    @git push origin $(git branch --show-current)

# Pull latest from main
pull-main:
    git checkout main
    git pull origin main
    git checkout -

# =============================================================================
# Kubernetes Development Environment
# =============================================================================

# Build Docker images for Kubernetes
k8s-build:
    @echo "Building Docker images for Kubernetes..."
    @bash k8s/scripts/build-images.sh --dev --prod

# Build development images only
k8s-build-dev:
    @echo "Building development images..."
    @bash k8s/scripts/build-images.sh --dev

# Build production images only
k8s-build-prod:
    @echo "Building production images..."
    @bash k8s/scripts/build-images.sh --prod

# Build and load images into kind
k8s-build-kind CLUSTER="aura-dev" TAG="dev":
    @echo "Building and loading images into kind cluster: {{CLUSTER}}"
    @bash k8s/scripts/build-images.sh --dev --tag {{TAG}}
    @bash k8s/scripts/load-images-kind.sh {{CLUSTER}} {{TAG}}

# Create kind cluster
k8s-cluster-create CLUSTER="aura-dev":
    @echo "Creating kind cluster: {{CLUSTER}}"
    @bash k8s/scripts/setup-kind.sh {{CLUSTER}}

# Delete kind cluster
k8s-cluster-delete CLUSTER="aura-dev":
    @echo "Deleting kind cluster: {{CLUSTER}}"
    kind delete cluster --name {{CLUSTER}} || echo "Cluster {{CLUSTER}} not found"

# Deploy to Kubernetes
k8s-deploy ENV="dev":
    @echo "Deploying to Kubernetes environment: {{ENV}}"
    @bash k8s/scripts/deploy.sh {{ENV}}

# Full workflow: build, load, deploy
k8s-dev CLUSTER="aura-dev" TAG="dev":
    @echo "Complete Kubernetes development workflow..."
    @just k8s-build-kind {{CLUSTER}} {{TAG}}
    @just k8s-deploy dev

# Push images to registry
k8s-push TAG="latest" OWNER="ofircohen205":
    @echo "Pushing images to GitHub Container Registry..."
    @bash k8s/scripts/push-images.sh --tag {{TAG}} --owner {{OWNER}}

# Setup complete development environment
k8s-dev-setup CLUSTER="aura-dev":
    @echo "Setting up complete Kubernetes development environment..."
    @bash k8s/scripts/dev-setup.sh {{CLUSTER}}

# Clean up development environment
k8s-dev-clean CLUSTER="aura-dev":
    @echo "Cleaning up Kubernetes development environment..."
    @bash k8s/scripts/dev-clean.sh {{CLUSTER}}

# Deploy monitoring stack (Loki, Prometheus, Grafana, AlertManager)
k8s-monitoring-setup:
    @echo "Deploying monitoring stack..."
    @bash k8s/scripts/setup-monitoring.sh

# Rollback deployment
k8s-rollback ENV="production" DEPLOYMENT="backend":
    @echo "Rolling back {{DEPLOYMENT}} in {{ENV}}..."
    @bash k8s/scripts/rollback.sh {{ENV}} {{DEPLOYMENT}}

# View pod status
k8s-status NAMESPACE="" SERVICE="":
    @bash k8s/scripts/pod-status.sh {{NAMESPACE}} {{SERVICE}}

# Run health checks for an environment
k8s-health-check ENV="dev" NAMESPACE="" TIMEOUT="30" RETRIES="5":
    @echo "Running health checks for {{ENV}} environment..."
    @if [ -z "{{NAMESPACE}}" ]; then \
        bash k8s/scripts/health-check.sh {{ENV}} "" {{TIMEOUT}} {{RETRIES}}; \
    else \
        bash k8s/scripts/health-check.sh {{ENV}} {{NAMESPACE}} {{TIMEOUT}} {{RETRIES}}; \
    fi
