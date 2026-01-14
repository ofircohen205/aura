# Software Requirements Specifications: Aura (The JIT Skill Agent)

## 1. System Architecture

The system follows a **Multi-Client Platform** architecture with a centralized semantic intelligence layer.

- **Clients**:
  - **IDE Agent**: VSCode Extension (TypeScript).
  - **CLI Guardian**: Terminal CLI (Python 3.11+).
  - **GitHub Architect**: Probot App (Serverless TypeScript).
  - **Knowledge Dashboard**: Web App (React/Next.js).
- **Backend**: FastAPI (Python 3.11+) serving as the orchestration layer.
- **Intelligence Engine**: LangGraph for stateful "Audit" and "Lesson" workflows.
- **Data Layer**: PostgreSQL (User/Team Data) and ChromaDB/Qdrant (Vector Store).

## 2. Technical Stack & Standards

### 2.1 Backend Core

- **Language**: Python 3.11+
- **Framework**: FastAPI (Async)
- **Orchestration**: LangGraph (Stateful Agents)
- **Database**: PostgreSQL (SQLAlchemy/Alembic)
- **Vector Store**: ChromaDB (Local/Dev) / Qdrant (Prod)

### 2.2 Clients

- **VSCode Support**: TypeScript, formatted with Prettier/ESLint.
- **CLI**: Python, built with `Typer` or `Click`. Shared models with Backend.
  - **Config**: `python-dotenv` for env vars, `PyYAML` for local config.
- **GitHub App**: Probot framework, deployed on Vercel/AWS Lambda.
- **Web Dashboard**: Next.js, Tailwind CSS, Shadcn UI.

## 3. Functional Specifications

### 3.1 The IDE Agent (Real-time)

- **Struggle Detection**:
  - Monitor `TextDocumentChangeEvent` for high-frequency edits (Levenshtein distance).
  - Trigger `struggle_detected` event to backend after 3 retries in 5m.
- **Snackable Lessons**:
  - Render Markdown + Mermaid diagrams in a WebView panel or Hover provider.

### 3.2 The CLI Guardian (Pre-commit)

- **Hook Interception**:
  - Wrap `git commit` and `git push` commands.
- **Local Audit**:
  - Run static analysis checks defined in `.aura/config.yaml`.
  - Block execution if critical "Architecture Violations" are found (e.g., direct DB calls in handlers).
- **Authentication & Config**:
  - **API Keys**: Load from `AURA_API_KEY` or `OPENAI_API_KEY` (env vars) or secure local file `~/.aura/credentials`.
  - **Local LLM Integration**:
    - Support `llm_provider` config (e.g., `openai`, `anthropic`, `ollama`).
    - Allow `llm_base_url` override (e.g., `http://localhost:11434` for Ollama).
  - **Fallback Strategy**: If Backend is unreachable, attempt Local LLM if configured.

### 3.3 The GitHub Architect (Async Review)

- **Diff Analysis**:
  - On `pull_request.opened`, fetch diff context.
- **Architectural Drift**:
  - Compare changes against Vector Store "Golden Paths".
  - Post comments ONLY if confidence > 85% to reduce noise.

### 3.4 The Knowledge Dashboard (Visualization)

- **Skill Tracking**:
  - Visualize user mastery based on accepted suggestions and successful audits.
- **Hotspot Analysis**:
  - Heatmap of files causing the most "Architectural Interventions".

## 4. Role Assignments & Implementation

Development tasks are assigned to the following roles from the `ai-coding-roles` registry.

### 4.1 Core Platform & AI [@[Senior Software Engineer](../ai-coding-roles/roles/core-development/senior-software-engineer.md), @[ML Engineer](../ai-coding-roles/roles/specialized-engineering/machine-learning-engineer.md)]

- **Task**: Implement LangGraph workflows for "Struggle Detection" and "Code Audit".
- **Task**: Set up RAG pipeline (ChromaDB ingestion) for "Golden Path" documentation.
- **Task**: Expose FastAPI endpoints for multi-client access.

### 4.2 Client Engineering [@[Senior Software Engineer](../ai-coding-roles/roles/core-development/senior-software-engineer.md)]

- **Task**: Build VSCode Extension host logic (LSP-like behavior).
- **Task**: Develop Python CLI with hook integration (Typer).
- **Task**: Implement CLI Config Manager for API Keys and Local LLM switching.
- **Task**: Implement Next.js Dashboard with Recharts/D3 for visualization.

### 4.3 Infrastructure & DevOps [@[DevOps Engineer](../ai-coding-roles/roles/infrastructure-operations/devops-engineer.md), @[Security Engineer](../ai-coding-roles/roles/quality-security/security-engineer.md)]

- **Task**: Configure CI/CD pipelines for 4 distinct artifacts (Ext, CLI, App, Web).
- **Task**: Ensure PII/Secrets are scrubbed before diffs are sent to the Backend (Security).
- **Task**: Manage Vercel/AWS deployment for the GitHub App and Dashboard.

## 5. Non-Functional Requirements

- **Performance**: CLI pre-commit checks must complete in <500ms (local) or <5s (network).
- **Privacy**: Code snippets are ephemeral; never stored persistently in the LLM logs.
- **Reliability**: GitHub App must handle rate limits gracefully using Redis queues.
