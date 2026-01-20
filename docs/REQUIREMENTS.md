# Aura Requirements Documentation

This document consolidates the Product Requirements Document (PRD), Software Requirements Specifications (SRS), and Customer Requirements Document (CRD) for Aura.

## Table of Contents

1. [Product Overview](#product-overview)
2. [Problem Statement](#problem-statement)
3. [Target Audience & Personas](#target-audience--personas)
4. [Key Pillars (Jobs To Be Done)](#key-pillars-jobs-to-be-done)
5. [System Architecture](#system-architecture)
6. [Technical Stack & Standards](#technical-stack--standards)
7. [Functional Requirements](#functional-requirements)
8. [Non-Functional Requirements](#non-functional-requirements)
9. [Success Metrics](#success-metrics)
10. [Role Assignments & Implementation](#role-assignments--implementation)

## Product Overview

"Aura" is an omni-channel JIT (Just-In-Time) Skill Agent designed to bridge the "Context Gap" between tribal knowledge and daily development. It systematically encodes architectural patterns and best practices, delivering them to developers across their entire workflow: in the IDE, at the Terminal, during Code Review, and on the Web.

## Problem Statement

**The "Context Gap" costs velocity and quality.**

Modern engineering teams face velocity and quality bottlenecks due to the disconnect between "how to code" (syntax) and "how _we_ code" (architecture).

- **The "Knowledge Gap":** AI coding tools (Cursor/Copilot) optimize for _completing the line_, often introducing patterns that violate project architecture (e.g., using `useEffect` where a Signal is required).
- **Documentation "Rot":** Best practices exist in `docs/` or separate Wikis but are disconnected from the editor. Developers don't context-switch to read them until PR review time—when it's too late.
- **The "Senior Bottleneck":** Senior engineers spend 30-40% of code review time repeating the same architectural guidance ("We use X instead of Y here because...").
- **Channel Fragmentation:** Insights learned in the IDE are lost when moving to the Terminal or reviewing code on GitHub.

## Target Audience & Personas

### The "Ramping" Developer (Junior/Mid or New Hire)

- **Mindset:** "I just want to get this ticket done without looking stupid."
- **Pain Point:** Fear of asking "basic" questions; overwhelmed by codebase size.
- **Needs:** A safe, automated "buddy" that whispers advice before they commit.

### The "Tech Lead" (Architect/Maintainer)

- **Mindset:** "I want to scale my mentorship without cloning myself."
- **Pain Point:** Seeing the same anti-patterns emerge in every Sprint; "Death by a thousand cuts."
- **Needs:** A way to encode "Tribal Knowledge" into "Active Rules" that execute automatically.

## Key Pillars (Jobs To Be Done)

### "The IDE Guide" (VSCode Extension)

**When** I am coding in real-time,  
**I want** the system to recognize when I'm "looping" (struggling) and offer the "Golden Path" snippet,  
**So that** I learn the right way to build before I even save the file.

**Details:**

- **Goal**: Education in real-time.
- **The Struggle Sensor**: Detects "looping" behavior (rewriting logic >3 times in 5 mins) and offers specific hints.
- **Architectural Guardrails**: Audits code diffs against "Golden Path" standards (e.g., suggesting proper state management libraries).
- **Snackable Lessons**: Delivers context via CodeLens, showing diagrams and explanations for complex patterns on hover.

**Technical Implementation:**

- Monitor `TextDocumentChangeEvent` for high-frequency edits (Levenshtein distance).
- Trigger `struggle_detected` event to backend after 3 retries in 5m.
- Render Markdown + Mermaid diagrams in a WebView panel or Hover provider.

### "The CLI Guardian" (Terminal Tool)

**When** I am running high-impact commands (e.g., `docker compose`, `git push`),  
**I want** Aura to verify my local environment/commands against project standards,  
**So that** I don't break the build or push suboptimal configurations.

**Details:**

- **Goal**: Safety before execution.
- **Function**: Intercepts high-impact commands (`git push`, `docker compose`) to verify local environment state and configuration compliance.
- **Value**: Prevents broken builds and suboptimal pushes by enforcing standards at the commit/deploy edge.

**Technical Implementation:**

- Wrap `git commit` and `git push` commands.
- Run static analysis checks defined in `.aura/config.yaml`.
- Block execution if critical "Architecture Violations" are found (e.g., direct DB calls in handlers).
- **Authentication & Config**:
  - **API Keys**: Load from `AURA_API_KEY` or `OPENAI_API_KEY` (env vars) or secure local file `~/.aura/credentials`.
  - **Local LLM Integration**:
    - Support `llm_provider` config (e.g., `openai`, `anthropic`, `ollama`).
    - Allow `llm_base_url` override (e.g., `http://localhost:11434` for Ollama).
  - **Fallback Strategy**: If Backend is unreachable, attempt Local LLM if configured.

### "The Reviewer-in-the-Loop" (GitHub App/Action)

**When** I submit a Pull Request,  
**I want** an automated architectural audit that explains _why_ a change is needed,  
**So that** the PR review process focuses on logic rather than style/standards.

**Details:**

- **Goal**: Automated architectural audit.
- **Function**: Analyzes Pull Requests for "architectural drift" and explains _why_ changes are needed.
- **Value**: Shifts human review focus from style/standards to core logic and design.

**Technical Implementation:**

- On `pull_request.opened`, fetch diff context.
- Compare changes against Vector Store "Golden Paths".
- Post comments ONLY if confidence > 85% to reduce noise.

### "The Skill Tree" (Web Dashboard)

**When** I want to track my professional growth or project health,  
**I want** a visual map of mastered patterns and architectural "hotspots,"  
**So that** I have a tangible record of my expanding expertise.

**Details:**

- **Goal**: Visualize growth and health.
- **Function**: Tracks user mastery of patterns and identifies architectural "hotspots" in the codebase.
- **Value**: Provides developers with a tangible record of expertise and leads with data on project health.

**Technical Implementation:**

- Visualize user mastery based on accepted suggestions and successful audits.
- Heatmap of files causing the most "Architectural Interventions".

## System Architecture

The system follows a **Multi-Client Platform** architecture with a centralized semantic intelligence layer.

- **Clients**:
  - **IDE Agent**: VSCode Extension (TypeScript).
  - **CLI Guardian**: Terminal CLI (Python 3.11+).
  - **GitHub Architect**: Probot App (Serverless TypeScript).
  - **Knowledge Dashboard**: Web App (React/Next.js).
- **Backend**: FastAPI (Python 3.11+) serving as the orchestration layer.
- **Intelligence Engine**: LangGraph for stateful "Audit" and "Lesson" workflows.
- **Data Layer**: PostgreSQL (User/Team Data) with pgvector extension (Vector Store).

## Technical Stack & Standards

### Backend Core

- **Language**: Python 3.11+
- **Framework**: FastAPI (Async)
- **Orchestration**: LangGraph (Stateful Agents)
- **Database**: PostgreSQL (SQLAlchemy/Alembic)
- **Vector Store**: pgvector (PostgreSQL extension, Production) / FAISS (Local/Dev)

### Clients

- **VSCode Support**: TypeScript, formatted with Prettier/ESLint.
- **CLI**: Python, built with `Typer` or `Click`. Shared models with Backend.
  - **Config**: `python-dotenv` for env vars, `PyYAML` for local config.
- **GitHub App**: Probot framework, deployed on Vercel/AWS Lambda.
- **Web Dashboard**: Next.js, Tailwind CSS, Shadcn UI.

## Functional Requirements

1. **In-Flow Education**: Interventions must occur in the specific context where work is happening (IDE, CLI, PR).
2. **Struggle Detection**: Intelligent inference of user difficulty based on edit patterns, time, and command history.
3. **Cross-Platform Sync**: A single "Knowledge Map" must start shared and synced across all four channels.
4. **Anti-AI Audit**: Specifically target and correct patterns commonly hallucinated or misapplied by unexpected LLM code generation.

## Non-Functional Requirements

- **Performance**: CLI pre-commit checks must complete in <500ms (local) or <5s (network).
- **Privacy**: Code snippets are ephemeral; never stored persistently in the LLM logs.
- **Reliability**: GitHub App must handle rate limits gracefully using Redis queues.

## Success Metrics

| Metric                             | Definition                                          | Goal     |
| :--------------------------------- | :-------------------------------------------------- | :------- |
| **Reduction in "Nit" PR Comments** | % of PR comments related to verified patterns       | **-40%** |
| **Junior Velocity**                | Average time to close first 5 tickets for new hires | **-20%** |
| **CLI Intervention Rate**          | % of "risky" commands caught and corrected          | **>15%** |
| **Pattern Adoption**               | % of new code using strict "Golden Path" libraries  | **>90%** |

## Role Assignments & Implementation

Development tasks are assigned to the following roles from the `ai-coding-roles` registry.

### Core Platform & AI

**Roles**: [Senior Software Engineer](../ai-coding-roles/roles/core-development/senior-software-engineer.md), [ML Engineer](../ai-coding-roles/roles/specialized-engineering/machine-learning-engineer.md)

- **Task**: Implement LangGraph workflows for "Struggle Detection" and "Code Audit".
- **Task**: Set up RAG pipeline (pgvector/FAISS ingestion) for "Golden Path" documentation.
- **Task**: Expose FastAPI endpoints for multi-client access.

### Client Engineering

**Role**: [Senior Software Engineer](../ai-coding-roles/roles/core-development/senior-software-engineer.md)

- **Task**: Build VSCode Extension host logic (LSP-like behavior).
- **Task**: Develop Python CLI with hook integration (Typer).
- **Task**: Implement CLI Config Manager for API Keys and Local LLM switching.
- **Task**: Implement Next.js Dashboard with Recharts/D3 for visualization.

### Infrastructure & DevOps

**Roles**: [DevOps Engineer](../ai-coding-roles/roles/infrastructure-operations/devops-engineer.md), [Security Engineer](../ai-coding-roles/roles/quality-security/security-engineer.md)

- **Task**: Configure CI/CD pipelines for 4 distinct artifacts (Ext, CLI, App, Web).
- **Task**: Ensure PII/Secrets are scrubbed before diffs are sent to the Backend (Security).
- **Task**: Manage Vercel/AWS deployment for the GitHub App and Dashboard.

## User Journey Example

1. **IDE**: Developer struggles to implement a feature; Aura suggests the correct pattern via CodeLens.
2. **CLI**: Developer attempts to `git push`; Aura audits the commit for restricted patterns (e.g., hardcoded secrets) and passes.
3. **PR**: Aura's GitHub bot comments on a subtle architectural mismatch, explaining the "Golden Path".
4. **Web**: Developer checks their dashboard, seeing they've "leveled up" in State Management patterns.
