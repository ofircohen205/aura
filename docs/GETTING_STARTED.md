# Getting Started with Aura

This guide will help you set up the Aura project for development. Aura is a polyglot monorepo containing Python (Backend, CLI, Core Libs) and TypeScript (Web Dashboard, VSCode Extension) components.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python**: >= 3.13
*   **Node.js**: >= 18.x (with npm)
*   **uv**: Python package manager (Required for Python components)
    *   [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
*   **Docker**: (Optional, for running the full stack)
*   **Just**: (Optional, generic command runner)
    *   [Install Just](https://github.com/casey/just#installation)

## Installation

### Using Just (Recommended)

If you have `just` installed, you can set up everything with a single command:

```bash
just install
```

This will install dependencies for both Python and Node.js projects.

### Manual Installation

If you prefer manual setup:

1.  **Python Dependencies**:
    Run from the root directory:
    ```bash
    uv sync
    ```

2.  **Node.js Dependencies**:
    Run from the root directory:
    ```bash
    npm install
    ```

## Running Components

### Backend (Python/FastAPI)

To run the backend development server:

**Using Just:**
```bash
just dev-backend
```

**Manually:**
```bash
cd apps/backend
uv run uvicorn src.main:app --reload
```

### Web Dashboard (Next.js)

To run the web dashboard:

**Using Just:**
```bash
just dev-web
```

**Manually:**
```bash
cd apps/web-dashboard
npm run dev
```

### CLI (Python)

The CLI component is located in `clients/cli`.

**To run the CLI during development:**

```bash
cd clients/cli
uv run aura --help
```

**Note**: Ensure the `aura` command is available in your virtual environment. If not, you may need to install the project in editable mode via `uv sync`.

### VSCode Extension

The VSCode extension is located in `clients/vscode`.

1.  **Navigate to the directory**:
    ```bash
    cd clients/vscode
    ```

2.  **Compile**:
    ```bash
    npm run compile
    ```
    Or watch for changes:
    ```bash
    npm run watch
    ```

3.  **Run**:
    Open the `clients/vscode` folder in VSCode and press `F5` to launch the Extension Development Host.

### Docker

To run the backend and potentially other services using Docker:

**Using Just:**
```bash
just docker-dev
```

**Manually:**
```bash
docker-compose -f docker/docker-compose.dev.yml up --build
```

## Project Structure

*   `apps/`
    *   `backend`: Python FastAPI application.
    *   `web-dashboard`: Next.js web application.
*   `clients/`
    *   `cli`: Python command-line interface.
    *   `vscode`: TypeScript VSCode extension.
*   `libs/`
    *   `core-py`: Shared Python business logic.
