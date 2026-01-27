FROM python:3.13-slim as base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy configuration files
COPY pyproject.toml uv.lock ./
COPY apps/backend/pyproject.toml apps/backend/
COPY libs/agentic-py/pyproject.toml libs/agentic-py/
COPY clients/cli/pyproject.toml clients/cli/

# Copy libs and apps source (needed for editable install in workspace)
COPY libs libs
COPY clients clients
COPY apps/backend apps/backend

# Install dependencies for the backend package
RUN uv sync --frozen --package backend

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/libs/agentic-py/src:/app/apps/backend/src:$PYTHONPATH"

# Development stage
FROM base as development
# Development dependencies are already installed via uv sync
# Volume mounts will be used for live code reloading

# Production stage
FROM base as production
# Production dependencies only
RUN uv sync --frozen --no-dev

# Run the application
CMD ["uv", "run", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
