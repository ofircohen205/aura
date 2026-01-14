# Linear Project Setup Summary

## Project Created: Aura

**Project ID**: `59b932cb-bd81-4890-bd7d-5c4c5617a34c`  
**URL**: https://linear.app/ofircohen/project/aura-65ac108335af

## Project Description

Aura is an AI-powered code analysis and learning platform that helps developers improve their coding skills through intelligent feedback, struggle detection, and personalized lessons.

### Key Features

1. **Struggle Detection Workflow** - Analyzes edit patterns to detect developer struggles
2. **Code Audit Workflow** - Performs static analysis and violation checking
3. **Event Ingestion** - Collects and processes development events
4. **RESTful API** - Well-structured API with proper error handling
5. **Web Dashboard** - Next.js dashboard for visualization
6. **VSCode Integration** - Extension for IDE integration
7. **CLI Tool** - Command-line interface for local analysis

## Issues Created

All issues have been moved to the Aura project and include comprehensive descriptions:

### Infrastructure & Setup

- **OFI-5**: Integrate Linear for Project Management and Development Pipeline
  - Status: Backlog
  - Labels: infrastructure, devops-engineer

### Core Features

- **OFI-6**: Implement LangGraph Workflows for Struggle Detection and Code Audit
  - Status: Backlog
  - Labels: backend, backend-engineer, ml

- **OFI-7**: Setup RAG Pipeline for Knowledge Retrieval
  - Status: Backlog
  - Labels: backend, backend-engineer, ml, ml-engineer

- **OFI-9**: Implement Authentication and Authorization
  - Status: Backlog
  - Labels: backend, backend-engineer, security-engineer

### Client Features

- **OFI-10**: Enhance Web Dashboard with Core Features
  - Status: Backlog
  - Labels: frontend, frontend-engineer

- **OFI-11**: Enhance VSCode Extension with Struggle Detection
  - Status: Backlog
  - Labels: frontend, frontend-engineer, vscode

- **OFI-12**: Implement CLI Guardian Pre-commit Hooks
  - Status: Backlog
  - Labels: cli, backend-engineer, security-engineer

### DevOps

- **OFI-8**: Configure CI/CD Pipelines for All Artifacts
  - Status: Backlog
  - Labels: devops-engineer, infrastructure

## Labels Created

Role-based labels for organizing work:

- `backend-engineer` - Backend/API development tasks
- `frontend-engineer` - Frontend/web development tasks
- `security-engineer` - Security-related tasks
- `devops-engineer` - Infrastructure and CI/CD tasks
- `qa-engineer` - Testing and quality assurance
- `software-architect` - Architecture decisions
- `ml-engineer` - Machine learning and AI tasks

Component labels:

- `backend` - Backend development
- `frontend` - Frontend development
- `cli` - CLI development
- `vscode` - VSCode extension
- `ml` - Machine learning
- `infrastructure` - Infrastructure tasks

## Issue Structure

Each issue includes:

1. **Objective** - Clear goal statement
2. **Background** - Context and rationale
3. **Requirements** - Detailed checklist of tasks
4. **Technical Details** - Architecture and implementation notes
5. **Dependencies** - Prerequisites and related work
6. **Acceptance Criteria** - Definition of done
7. **Related Files** - Code locations and documentation
8. **Story Reference** - Links to detailed story documents

## Next Steps

1. **Review Issues** - Check all issues in Linear project
2. **Prioritize** - Set priorities and assign to sprints
3. **Break Down** - Create sub-issues for large features
4. **Start Development** - Follow the development pipeline

## Development Pipeline

All development follows the 9-stage pipeline:

1. Read Task/Story (from Linear)
2. Plan Sub-tasks
3. Create Branch (`feature/OFI-XXX-description`)
4. Implement (using role-based development)
5. Write Tests
6. Code Review
7. Fix Issues
8. Commit & Push
9. Create PR (with Linear link)

See `docs/workflows/development-pipeline.md` for details.

## Viewing Issues

- **Linear Web**: https://linear.app/ofircohen/project/aura-65ac108335af
- **In Cursor**: Use Linear MCP tools to view and manage issues
- **Issue Format**: `OFI-XXX` (e.g., `OFI-5`, `OFI-6`)

## Branch Naming

Use Linear issue IDs in branch names:

```bash
feature/OFI-6-langgraph-workflows
fix/OFI-9-auth-bug
refactor/OFI-10-dashboard-structure
```

## Commit Messages

Include Linear issue ID in commits:

```bash
git commit -m "feat(workflows): implement struggle detection [OFI-6]"
```

## PR Descriptions

Link to Linear issues:

```markdown
Closes OFI-6

Implements LangGraph workflows for struggle detection and code audit.
```
