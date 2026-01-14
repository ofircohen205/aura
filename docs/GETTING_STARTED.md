# Getting Started with Aura

This guide will help you set up the Aura project for development. Aura is a polyglot monorepo containing Python (Backend, CLI, Core Libs) and TypeScript (Web Dashboard, VSCode Extension) components.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: >= 20.10 (Required)
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: >= 2.0 (Required)
  - Usually included with Docker Desktop
- **Just**: (Optional, but recommended for convenient commands)
  - [Install Just](https://github.com/casey/just#installation)

> **Note**: This project uses Docker-only development. You don't need to install Python, Node.js, uv, or npm locally. Everything runs in Docker containers.

## Installation

No installation needed! Everything runs in Docker.

### Quick Start

```bash
# Start all development services
just dev
```

That's it! The Docker setup will:

- Build all containers
- Install all dependencies
- Start all services
- Set up the database

### First Time Setup

On first run, Docker will:

1. Build container images
2. Install Python dependencies (via uv)
3. Install Node.js dependencies (via npm)
4. Run database migrations
5. Start all services

This may take a few minutes. Subsequent starts are much faster.

## Configuration

### Environment Variables

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
```

For production, use `.env.production` or set environment variables directly. The configuration system supports:

- `.env.local` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Set the `ENVIRONMENT` variable to select which config file to use.

## Running Components

All components run automatically when you start the development environment:

```bash
just dev
```

This starts:

- **Backend API** on `http://localhost:8000`
- **Web Dashboard** on `http://localhost:3000`
- **PostgreSQL** database on `localhost:5432`
- **Development Tools** container for running commands

### Accessing Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
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

## Project Structure

- `apps/`
  - `backend`: Python FastAPI application.
  - `web-dashboard`: Next.js web application.
- `clients/`
  - `cli`: Python command-line interface.
  - `vscode`: TypeScript VSCode extension.
- `libs/`
  - `core-py`: Shared Python business logic.
