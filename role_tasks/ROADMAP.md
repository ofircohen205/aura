# Project Roadmap & Task Orchestration

This document tracks the high-level progress of all roles and defines the critical path for development.

## 1. Foundation (Phase 0)

- [x] **Define Project Structure** (Software Architect)
  - _Output_: Monorepo structure (apps, libs, clients), `uv` & `npm` workspaces, Docker config.
  - _Next Steps_: Initialize Core Libraries and specific Applications.

## 2. Core Implementation (Phase 1)

These tasks can be executed in parallel after Phase 0.

### Backend & CLI

- [x] **Develop Python CLI** (Senior Software Engineer)
  - _Story_: `role_tasks/senior-software-engineer/stories/develop-python-cli.md`
  - _Dependencies_: `libs/agentic-py`
  - _Goal_: Implement the "Guardian" CLI for local code analysis.
- [x] **Expose FastAPI Endpoints** (Senior Software Engineer)
  - _Story_: `role_tasks/senior-software-engineer/stories/expose-fastapi-endpoints.md`
  - _Dependencies_: `libs/agentic-py`
  - _Goal_: Create the orchestration layer for the web dashboard.

### Client Side

- [x] **Build VSCode Extension Host** (Senior Software Engineer)
  - _Story_: `role_tasks/senior-software-engineer/stories/build-vscode-extension-host.md`
  - _Dependencies_: `clients/vscode`
  - _Goal_: Basic VSCode extension structure communicating with the CLI/LSP.

## 3. Advanced Features (Phase 2)

Dependent on Core Implementation.

- [ ] **Implement LangGraph Workflows** (Senior Software Engineer)
  - _Story_: `role_tasks/senior-software-engineer/stories/implement-langgraph-workflows.md`
  - _Dependencies_: Backend, Vector DB
- [ ] **Setup RAG Pipeline** (Senior Software Engineer)
  - _Story_: `role_tasks/senior-software-engineer/stories/setup-rag-pipeline.md`
  - _Dependencies_: Backend, LangGraph

## 4. Operations & Security (Parallel/Ongoing)

- [ ] **Configure CI/CD Pipelines** (DevOps Engineer)
  - _Story_: `role_tasks/devops-engineer/stories/configure-cicd-pipelines.md`
- [ ] **Ensure Security** (Security Engineer)
  - _Story_: `role_tasks/security-engineer/stories/ensure-security.md`
- [ ] **Collaborate on AI Workflows** (Machine Learning Engineer)
  - _Story_: `role_tasks/machine-learning-engineer/stories/collaborate-ai-workflows.md`

## Next Action Selection

**Recommended Immediate Next Task:** `Develop Python CLI` or `Expose FastAPI Endpoints`.
These build the foundational logic in `libs/agentic-py` that other components (VSCode, RAG) will rely on.
