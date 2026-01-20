# Aura User Guide

Welcome to the Aura User Guide! This comprehensive guide will help you understand and use all features of the Aura platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Documentation](#api-documentation)
3. [CLI Usage](#cli-usage)
4. [VSCode Extension](#vscode-extension)
5. [Workflows](#workflows)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Quick Start

Aura is a code analysis and developer assistance platform that helps you:

- Detect when developers are struggling and provide helpful lessons
- Audit code changes for violations and best practices
- Track development events and patterns

### Installation

Aura runs entirely in Docker containers, so you don't need to install Python, Node.js, or other dependencies locally.

**Prerequisites:**

- Docker >= 20.10
- Docker Compose >= 2.0
- Just (optional, for convenient commands)

**Start the development environment:**

```bash
just dev
```

This will:

- Build all containers
- Install all dependencies
- Start all services (backend, web dashboard, database)
- Run database migrations

### Accessing Services

Once started, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)
- **Web Dashboard**: http://localhost:3000
- **Database**: localhost:5432 (default credentials for local dev only)

## API Documentation

The Aura API is a RESTful API built with FastAPI. All endpoints are versioned under `/api/v1/`.

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

The API uses JWT-based authentication. See [Authentication API](#authentication-api) section below for detailed authentication endpoints and flows.

### Endpoints

#### Workflows API

The Workflows API manages LangGraph-based workflows for code analysis and struggle detection.

##### 1. Trigger Struggle Detection Workflow

Detects if a developer is struggling based on edit frequency and error patterns.

**Endpoint:** `POST /api/v1/workflows/struggle`

**Request Body:**

```json
{
  "edit_frequency": 15.5,
  "error_logs": [
    "TypeError: Cannot read property 'x' of undefined",
    "SyntaxError: Unexpected token"
  ],
  "history": ["Previous attempt 1", "Previous attempt 2"]
}
```

**Response:**

```json
{
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "state": {
    "edit_frequency": 15.5,
    "error_logs": ["TypeError: Cannot read property 'x' of undefined"],
    "history": ["Previous attempt 1"],
    "is_struggling": true,
    "lesson_recommendation": "Based on your error patterns, you're encountering type-related issues..."
  }
}
```

**Status Codes:**

- `200 OK`: Workflow completed successfully
- `500 Internal Server Error`: Workflow execution failed
- `503 Service Unavailable`: Database connection unavailable

##### 2. Trigger Code Audit Workflow

Performs static analysis on code changes to detect violations against coding standards.

**Endpoint:** `POST /api/v1/workflows/audit`

**Request Body:**

```json
{
  "diff_content": "diff --git a/src/main.py b/src/main.py\n@@ -1,3 +1,5 @@\n def hello():\n+    print('Hello')\n     return 'world'\n",
  "violations": []
}
```

**Response:**

```json
{
  "thread_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "state": {
    "diff_content": "...",
    "violations": [
      "Avoid using print statements in production code. Use logging instead."
    ],
    "status": "fail",
    "parsed_files": [...],
    "violation_details": [...]
  }
}
```

**Status Codes:**

- `200 OK`: Audit completed successfully
- `400 Bad Request`: Invalid input (e.g., diff content too large, max 10MB)
- `500 Internal Server Error`: Workflow execution failed
- `503 Service Unavailable`: Database connection unavailable

**Limits:**

- Maximum diff content size: 10MB (10,000,000 characters)

##### 3. Get Workflow State

Retrieves the current state of a workflow by thread ID.

**Endpoint:** `GET /api/v1/workflows/{thread_id}`

**Path Parameters:**

- `thread_id` (string, required): Unique thread identifier (UUID format)

**Response:**

```json
{
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "state": {
    "is_struggling": true,
    "lesson_recommendation": "..."
  }
}
```

**Status Codes:**

- `200 OK`: Workflow state retrieved successfully
- `404 Not Found`: Workflow not found
- `503 Service Unavailable`: Database connection unavailable

#### Events API

The Events API ingests events from various clients (VSCode extension, CLI, GitHub app).

##### Ingest Event

**Endpoint:** `POST /api/v1/events/`

**Request Body:**

```json
{
  "source": "vscode",
  "type": "error_logged",
  "data": {
    "error_message": "TypeError: ...",
    "file": "src/main.py",
    "line": 42
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**

```json
{
  "status": "processed",
  "event_id": "evt_1234567890",
  "processed_at": "2024-01-15T10:30:01Z"
}
```

**Status Codes:**

- `200 OK`: Event ingested successfully
- `400 Bad Request`: Invalid event data
- `500 Internal Server Error`: Event processing failed

#### Authentication API

The Authentication API provides user registration, login, token management, and user profile endpoints.

##### Public Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate and receive tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Revoke refresh token

##### Protected Endpoints

- `GET /api/v1/auth/me` - Get current user profile
- `PATCH /api/v1/auth/me` - Update current user profile

##### Admin Endpoints

- `GET /api/v1/auth/users` - List users (paginated)
- `POST /api/v1/auth/users/bulk` - Bulk create users
- `PATCH /api/v1/auth/users/bulk` - Bulk update users
- `DELETE /api/v1/auth/users/bulk` - Bulk delete users

**Authentication Flow:**

1. **Registration**: User creates account with email, username, password
2. **Login**: User authenticates and receives access + refresh tokens
3. **API Requests**: Include access token in `Authorization: Bearer <token>` header
4. **Token Refresh**: Use refresh token to get new access token when expired
5. **Logout**: Revoke refresh token to invalidate session

**Security Features:**

- Password Hashing: Bcrypt with 12 rounds
- JWT Tokens: HS256 algorithm with configurable expiration
- Refresh Tokens: Stored in Redis with TTL
- CSRF Protection: Double-submit cookie pattern
- Security Headers: HSTS, CSP, X-Frame-Options, etc.
- Rate Limiting: Token bucket algorithm with Redis

**Examples:**

Register User:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Get Current User:

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

#### Audit API

The Audit API provides a simple interface for triggering code audits.

##### Trigger Audit

**Endpoint:** `GET /api/v1/audit/?repo_path=/path/to/repo`

**Query Parameters:**

- `repo_path` (string, required): Path to the repository to audit

**Response:**

```json
{
  "status": "started",
  "repo": "/path/to/repo",
  "message": "Audit process initiated"
}
```

**Status Codes:**

- `200 OK`: Audit started successfully
- `400 Bad Request`: Invalid repository path
- `500 Internal Server Error`: Audit execution failed

### Health Check Endpoints

##### Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "ok",
  "database": "connected"
}
```

##### Cache Health Check

**Endpoint:** `GET /health/cache`

**Response:**

```json
{
  "status": "ok",
  "cache": {
    "enabled": true,
    "type": "memory",
    "hits": 150,
    "misses": 50,
    "size": 100
  }
}
```

### Error Responses

All error responses follow a consistent format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "type": "ErrorType",
    "status_code": 400,
    "path": "/api/v1/workflows/audit",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
    "details": {
      "additional": "error details"
    }
  }
}
```

### Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per 60 seconds per client
- **Struggle Workflow**: 50 requests per 60 seconds
- **Audit Workflow**: 30 requests per 60 seconds

Rate limit information is included in response headers:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Window`: Time window in seconds
- `X-RateLimit-Remaining`: Remaining requests in current window

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response with a `Retry-After` header.

## CLI Usage

The Aura CLI (Guardian) provides command-line tools for code auditing and git hook management.

### Installation

The CLI is included in the Aura monorepo. To use it:

```bash
# Get shell in dev container
just docker-shell

# Navigate to CLI directory
cd clients/cli

# Run CLI commands
uv run aura --help
```

### Commands

#### Configuration

View current configuration:

```bash
aura config
```

This displays:

- Configuration file path
- Current settings (API key, etc.)

#### Audit

Run code audits:

```bash
# Audit all changes
aura audit run

# Audit only staged files
aura audit run --staged
```

The audit command:

- Analyzes code changes
- Checks for violations
- Returns exit code 0 if all checks pass, 1 if issues found

#### Git Hooks

Install pre-commit hook:

```bash
aura hook install
```

This installs a pre-commit git hook that automatically runs `aura audit --staged` before each commit. The commit will be blocked if the audit fails.

**Note:** The hook must be installed in a git repository (requires `.git` directory).

### Example Workflow

```bash
# 1. Install git hook (one-time setup)
aura hook install

# 2. Make code changes
git add src/main.py

# 3. Commit (hook automatically runs audit)
git commit -m "Add new feature"
# 🛡️  Aura Guard: Auditing changes...
# ✅ Aura Audit Passed.
```

## VSCode Extension

The Aura VSCode extension provides real-time code analysis and struggle detection within your editor.

### Installation

1. Navigate to `clients/vscode` directory
2. Install dependencies:
   ```bash
   npm install
   ```
3. Open in VSCode and press `F5` to launch Extension Development Host

### Features

- Real-time code analysis
- Struggle detection based on edit patterns
- Error log tracking
- Lesson recommendations

### Usage

The extension automatically:

- Tracks your editing patterns
- Monitors error logs
- Detects when you're struggling
- Provides contextual lesson recommendations

## Workflows

Aura uses LangGraph workflows to orchestrate complex analysis tasks.

### Struggle Detection Workflow

**Purpose:** Detects when developers are struggling and provides personalized lesson recommendations.

**How it works:**

1. Analyzes edit frequency (high frequency may indicate confusion)
2. Examines error logs for patterns
3. Considers previous attempt history
4. Uses thresholds to determine if struggling:
   - Edit frequency > threshold (default: configurable)
   - Error count > threshold (default: configurable)
5. If struggling detected, generates lesson recommendation using:
   - Error patterns
   - RAG (Retrieval-Augmented Generation) for relevant documentation
   - LLM for personalized lesson generation

**State Structure:**

```python
{
  "edit_frequency": float,
  "error_logs": list[str],
  "history": list[str],
  "is_struggling": bool,
  "lesson_recommendation": str | None
}
```

### Code Audit Workflow

**Purpose:** Performs static analysis on code changes to detect violations.

**How it works:**

1. Parses git diff content
2. Extracts file information and code hunks
3. Performs AST-based analysis (for Python files)
4. Runs pattern-based checks (for all files)
5. Filters false positives using context-aware heuristics
6. Uses LLM for ambiguous violation analysis (when enabled)
7. Returns violations with details and remediation suggestions

**State Structure:**

```python
{
  "diff_content": str,
  "violations": list[str],
  "status": str,  # "pass", "fail", "remediation_required"
  "parsed_files": list[dict],
  "parsed_hunks": list[dict],
  "violation_details": list[dict]
}
```

**Detected Violations:**

- Print statements in production code
- Debugger calls (pdb, ipdb, breakpoint)
- Long functions (configurable threshold)
- Hardcoded secrets (passwords, API keys, tokens)

## Configuration

### Environment Variables

Aura uses environment-based configuration. Create a `.env.local` file in the project root:

```bash
# Environment
ENVIRONMENT=local

# Database Configuration
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

# LLM Configuration (optional)
LLM_ENABLED=false
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
OPENAI_API_KEY=your-api-key-here

# RAG Configuration (optional)
RAG_ENABLED=false
VECTOR_STORE_TYPE=pgvector  # or "faiss" for local dev
PGVECTOR_CONNECTION_STRING=postgresql://user:pass@localhost/db
PGVECTOR_COLLECTION=aura_knowledge_base

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache Configuration
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600
LLM_CACHE_MAX_SIZE=1000
```

### Configuration Files

The system supports multiple environment files:

- `.env.local` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Set the `ENVIRONMENT` variable to select which config file to use.

### Database Setup

**PostgreSQL with pgvector:**

1. Install PostgreSQL
2. Install pgvector extension:
   ```sql
   CREATE EXTENSION vector;
   ```
3. Configure connection string in `.env.local`

**For local development with FAISS:**

Set `VECTOR_STORE_TYPE=faiss` and configure `FAISS_INDEX_PATH`.

### Vector Store Configuration

Aura supports two vector store backends:

1. **pgvector** (Production): PostgreSQL extension for vector storage
   - Requires PostgreSQL with pgvector extension
   - Better for production (ACID guarantees, single database)
   - Configure via `PGVECTOR_CONNECTION_STRING`

2. **FAISS** (Local Development): In-memory vector store
   - No database required
   - Fast for local development
   - Configure via `FAISS_INDEX_PATH`

## Troubleshooting

### Common Issues

#### Database Connection Failed

**Symptoms:** Health check returns `503 Service Unavailable`

**Solutions:**

1. Verify PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```
2. Check connection string in `.env.local`
3. Verify database exists:
   ```bash
   docker exec -it <postgres-container> psql -U aura -d aura_db
   ```

#### Rate Limit Exceeded

**Symptoms:** `429 Too Many Requests` responses

**Solutions:**

1. Wait for the rate limit window to reset (check `Retry-After` header)
2. Reduce request frequency
3. Use batch endpoints when available
4. Disable rate limiting for development (set `RATE_LIMIT_ENABLED=false`)

#### Workflow Not Found

**Symptoms:** `404 Not Found` when retrieving workflow state

**Solutions:**

1. Verify the `thread_id` is correct (must be valid UUID)
2. Check if workflow completed and was cleaned up
3. Verify database connectivity

#### LLM Errors

**Symptoms:** LLM-related errors in logs or workflow failures

**Solutions:**

1. Verify `OPENAI_API_KEY` is set correctly
2. Check API quota and rate limits
3. Verify `LLM_ENABLED=true` if using LLM features
4. Check network connectivity to OpenAI API

#### RAG Service Not Available

**Symptoms:** Empty context or "RAG service is not enabled" messages

**Solutions:**

1. Set `RAG_ENABLED=true` in environment
2. Verify vector store configuration
3. For pgvector: Ensure extension is installed
4. For FAISS: Ensure index path exists and is accessible

### Debugging Tips

#### Enable Debug Logging

Set in `.env.local`:

```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

#### Check Logs

```bash
# View backend logs
just dev-logs

# Or in Docker
docker-compose -f docker/docker-compose.dev.yml logs -f backend
```

#### Test API Endpoints

Use the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Verify Configuration

```bash
# Check backend configuration
curl http://localhost:8000/health

# Check cache status
curl http://localhost:8000/health/cache
```

### Getting Help

- Check the [Development Documentation](DEVELOPMENT.md)
- Review [Architecture Guide](ARCHITECTURE.md)
- Open an issue on GitHub
- Check logs for detailed error messages

---

**Last Updated:** 2026-01-20
