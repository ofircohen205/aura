# Story: Define Project Structure and Monorepo Layout

**GitHub Issue**: #3

**Role:** Software Architect
**Related SRS Section:** 1, 2

## Desired Feature

Establish a **Polyglot Monorepo** structure that maximizes code reuse between components while maintaining clean separation. The system has both Python (Backend, CLI) and TypeScript (VSCode, Web, GitHub App) components. We need a unified strategy for dependency management and shared logic.

## Planning & Technical Spec

### Architecture Strategy

Refer to `docs/ARCHITECTURE.md` for detailed internal structure of Backend, Frontend, CLI, and VSCode Extension.

- **Python Stack**: Use `uv` for extremely fast dependency management and workspace support.
  - **Workspace Root**: `pyproject.toml` at the root.
  - **Members**: `backend`, `clients/cli`, `libs/agentic-py`.
- **TypeScript Stack**: Use `npm` (or `pnpm`) workspaces.
  - **Workspace Root**: `package.json` at the root.
  - **Members**: `clients/vscode`, `clients/web`, `clients/github-app`, `libs/shared-ts`.

### Proposed Layout

```text
aura/
├── pyproject.toml        # Root uv workspace definition
├── uv.lock
├── package.json          # Root npm workspace definition
├── apps/
│   ├── backend/          # FastAPI orchestration layer (Python)
│   └── web-dashboard/    # Next.js Dashboard (TypeScript)
├── clients/
│   ├── vscode/           # VSCode Extension (TypeScript)
│   ├── cli/              # Guardian CLI (Python)
│   └── github-app/       # Probot App (TypeScript)
├── libs/
│   ├── agentic-py/          # Shared Python logic (Audits, Struggle heuristics) - CRITICAL for sharing between CLI & Backend
│   └── shared-ts/        # Shared Types/Schemas (if needed)
├── docs/                 # Architecture decision records
└── docker/
    ├── docker-compose.dev.yml   # Local dev orchestration
    └── docker-compose.prod.yml  # Production orchestration
```

### Why this structure?

1.  **Shared Logic**: The "Guardian" CLI and the Backend "Audit" workflow share the _same_ static analysis rules. Using a shared `libs/agentic-py` library within a `uv` workspace ensures they use identical logic without code duplication.
2.  **Performance**: `uv` is significantly faster than `poetry` and simplifies CI/CD.
3.  **Organization**: Separating `apps` (server-side/webapp) from `clients` (user-side tools) can provide mental clarity, though a flat list is also acceptable. Grouping by language (Python vs TS) is an alternative, but functional grouping (`libs` vs deployables) is usually better for scaling.

### Standards & Workflows

- **Git Flow**: Create a new branch for this story and work only on that branch.
- **Issue Updates**: Reference the GitHub Issue (check header) in your commits and PRs.

### Implementation Checklist

- [x] Initialize root with `uv init --workspace`.
- [x] Create `libs/agentic-py` package.
- [x] Initialize `apps/backend` dependent on `libs/agentic-py`.
- [x] Initialize `clients/cli` dependent on `libs/agentic-py`.
- [x] Initialize `apps/web-dashboard` and other TS projects.
- [x] Create `docker/` directory.
- [x] Create `docker/docker-compose.dev.yml` and `docker/docker-compose.prod.yml`.
- [x] Create `README.md` documenting the dual-workspace setup.

## Testing Plan

- **Manual Verification**:
  - [x] `uv sync` installs all python dependencies for all members.
  - [x] `npm install` installs all node modules.
  - [x] Verify imports work: `from aura_core import audit` works in both Backend and CLI.
