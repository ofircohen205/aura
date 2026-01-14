# Product Requirements Document: Aura (The JIT Skill Agent)

## 1. Product Overview

"Aura" is an omni-channel JIT (Just-In-Time) Skill Agent designed to bridge the "Context Gap" between tribal knowledge and daily development. It systematically encodes architectural patterns and best practices, delivering them to developers across their entire workflow: in the IDE, at the Terminal, during Code Review, and on the Web.

## 2. Problem Statement

Modern engineering teams face velocity and quality bottlenecks due to the disconnect between "how to code" (syntax) and "how _we_ code" (architecture).

- **Knowledge Gap**: AI tools often generate syntactically correct but architecturally non-compliant code.
- **Documentation Rot**: Best practices live in disconnected wikis, ignored until it's too late.
- **Senior Bottleneck**: Tech leads waste time repeating the same architectural advice in code reviews.

## 3. Target Audience & Personas

- **The Ramping Developer**: Junior/Mid engineers who want to contribute effectively without "looking stupid" or breaking patterns. They need a safe "buddy" to guide them.
- **The Tech Lead**: Architects who want to scale mentorship and ensure consistency without micromanaging every PR.

## 4. Key Pillars (Jobs To Be Done)

### 4.1 "The IDE Guide" (VSCode Extension)

- **Goal**: Education in real-time.
- **The Struggle Sensor**: Detects "looping" behavior (rewriting logic >3 times in 5 mins) and offers specific hints.
- **Architectural Guardrails**: Audits code diffs against "Golden Path" standards (e.g., suggesting proper state management libraries).
- **Snackable Lessons**: Delivers context via CodeLens, showing diagrams and explanations for complex patterns on hover.

### 4.2 "The CLI Guardian" (Terminal Tool)

- **Goal**: Safety before execution.
- **Function**: Intercepts high-impact commands (`git push`, `docker compose`) to verify local environment state and configuration compliance.
- **Value**: Prevents broken builds and suboptimal pushes by enforcing standards at the commit/deploy edge.

### 4.3 "The Reviewer-in-the-Loop" (GitHub App/Action)

- **Goal**: Automated architectural audit.
- **Function**: Analyzes Pull Requests for "architectural drift" and explains _why_ changes are needed.
- **Value**: Shifts human review focus from style/standards to core logic and design.

### 4.4 "The Skill Tree" (Web Dashboard)

- **Goal**: Visualize growth and health.
- **Function**: Tracks user mastery of patterns and identifies architectural "hotspots" in the codebase.
- **Value**: Provides developers with a tangible record of expertise and leads with data on project health.

## 5. Functional Requirements

1.  **In-Flow Education**: Interventions must occur in the specific context where work is happening (IDE, CLI, PR).
2.  **Struggle Detection**: Intelligent inference of user difficulty based on edit patterns, time, and command history.
3.  **Cross-Platform Sync**: A single "Knowledge Map" must start shared and synced across all four channels.
4.  **Anti-AI Audit**: Specifically target and correct patterns commonly hallucinated or misapplied by unexpected LLM code generation.

## 6. Success Metrics

| Metric                                                              | Goal     |
| :------------------------------------------------------------------ | :------- |
| **Reduction in "Nit" PR Comments** (% related to verified patterns) | **-40%** |
| **Junior Velocity** (Time to close first 5 tickets)                 | **-20%** |
| **CLI Intervention Rate** (% "risky" commands caught)               | **>15%** |
| **Pattern Adoption** (% new code using Golden Path)                 | **>90%** |

## 7. User Journey Example

1.  **IDE**: Developer struggles to implement a feature; Aura suggests the correct pattern via CodeLens.
2.  **CLI**: Developer attempts to `git push`; Aura audits the commit for restricted patterns (e.g., hardcoded secrets) and passes.
3.  **PR**: Aura's GitHub bot comments on a subtle architectural mismatch, explaining the "Golden Path".
4.  **Web**: Developer checks their dashboard, seeing they've "leveled up" in State Management patterns.
