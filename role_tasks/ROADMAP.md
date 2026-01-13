# Project Roadmap & Task Orchestration

This document tracks the high-level progress of all roles and defines the critical path for development.

## 1. Foundation (Phase 0)
- [x] **Define Project Structure** (Software Architect)
    - *Output*: Monorepo structure (apps, libs, clients), `uv` & `npm` workspaces, Docker config.
    - *Next Steps*: Initialize Core Libraries and specific Applications.

## 2. Core Implementation (Phase 1)
These tasks can be executed in parallel after Phase 0.

### Backend & CLI
- [x] **Develop Python CLI** (Senior Software Engineer)
    - *Story*: `role_tasks/senior-software-engineer/stories/develop-python-cli.md`
    - *Dependencies*: `libs/core-py`
    - *Goal*: Implement the "Guardian" CLI for local code analysis.
- [x] **Expose FastAPI Endpoints** (Senior Software Engineer)
    - *Story*: `role_tasks/senior-software-engineer/stories/expose-fastapi-endpoints.md`
    - *Dependencies*: `libs/core-py`
    - *Goal*: Create the orchestration layer for the web dashboard.

### Client Side
- [x] **Build VSCode Extension Host** (Senior Software Engineer)
    - *Story*: `role_tasks/senior-software-engineer/stories/build-vscode-extension-host.md`
    - *Dependencies*: `clients/vscode`
    - *Goal*: Basic VSCode extension structure communicating with the CLI/LSP.

## 3. Advanced Features (Phase 2)
Dependent on Core Implementation.

- [ ] **Implement LangGraph Workflows** (Senior Software Engineer)
    - *Story*: `role_tasks/senior-software-engineer/stories/implement-langgraph-workflows.md`
    - *Dependencies*: Backend, Vector DB
- [ ] **Setup RAG Pipeline** (Senior Software Engineer)
    - *Story*: `role_tasks/senior-software-engineer/stories/setup-rag-pipeline.md`
    - *Dependencies*: Backend, LangGraph

## 4. Operations & Security (Parallel/Ongoing)
- [ ] **Configure CI/CD Pipelines** (DevOps Engineer)
    - *Story*: `role_tasks/devops-engineer/stories/configure-cicd-pipelines.md`
- [ ] **Ensure Security** (Security Engineer)
    - *Story*: `role_tasks/security-engineer/stories/ensure-security.md`
- [ ] **Collaborate on AI Workflows** (Machine Learning Engineer)
    - *Story*: `role_tasks/machine-learning-engineer/stories/collaborate-ai-workflows.md`

## Next Action Selection
**Recommended Immediate Next Task:** `Develop Python CLI` or `Expose FastAPI Endpoints`.
These build the foundational logic in `libs/core-py` that other components (VSCode, RAG) will rely on.
