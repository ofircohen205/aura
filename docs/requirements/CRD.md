# Customer Requirements Document: Aura (The JIT Skill Agent)

## 1. Problem Statement
**The "Context Gap" costs velocity and quality.**
In modern engineering teams, "how to code" (syntax) is easy, but "how *we* code" (architecture/patterns) is tribal knowledge.
* **The "Knowledge Gap":** AI coding tools (Cursor/Copilot) optimize for *completing the line*, often introducing patterns that violate project architecture (e.g., using `useEffect` where a Signal is required).
* **Documentation "Rot":** Best practices exist in `docs/` or separate Wikis but are disconnected from the editor. Developers don't context-switch to read them until PR review time—when it's too late.
* **The "Senior Bottleneck":** Senior engineers spend 30-40% of code review time repeating the same architectural guidance ("We use X instead of Y here because...").
* **Channel Fragmentation:** Insights learned in the IDE are lost when moving to the Terminal or reviewing code on GitHub.

## 2. Target Audience & Personas

### 2.1 The "Ramping" Developer (Junior/Mid or New Hire)
* **Mindset:** "I just want to get this ticket done without looking stupid."
* **Pain Point:** Fear of asking "basic" questions; overwhelmed by codebase size.
* **Needs:** A safe, automated "buddy" that whispers advice before they commit.

### 2.2 The "Tech Lead" (Architect/Maintainer)
* **Mindset:** "I want to scale my mentorship without cloning myself."
* **Pain Point:** Seeing the same anti-patterns emerge in every Sprint; "Death by a thousand cuts."
* **Needs:** A way to encode "Tribal Knowledge" into "Active Rules" that execute automatically.

## 3. The Omni-Channel Experience (Jobs To Be Done)

### 3.1 "The IDE Guide" (VSCode Extension)
**When** I am coding in real-time,
**I want** the system to recognize when I'm "looping" (struggling) and offer the "Golden Path" snippet,
**So that** I learn the right way to build before I even save the file.

### 3.2 "The CLI Guardian" (Terminal Tool)
**When** I am running high-impact commands (e.g., `docker compose`, `git push`),
**I want** Aura to verify my local environment/commands against project standards,
**So that** I don't break the build or push suboptimal configurations.

### 3.3 "The Reviewer-in-the-Loop" (GitHub App/Action)
**When** I submit a Pull Request,
**I want** an automated architectural audit that explains *why* a change is needed,
**So that** the PR review process focuses on logic rather than style/standards.

### 3.4 "The Skill Tree" (Web Dashboard)
**When** I want to track my professional growth or project health,
**I want** a visual map of mastered patterns and architectural "hotspots,"
**So that** I have a tangible record of my expanding expertise.

## 4. Key Functional Requirements
* **In-Flow Education:** Interventions happen *where the work is* (IDE, CLI, PR).
* **Struggle Detection:** Inference based on edits/time/command history.
* **Cross-Platform Sync:** A single "Knowledge Map" shared across all 4 channels.
* **Anti-AI Audit:** Auditing code specifically for architectural drift introduced by LLM generators.

## 5. Success Criteria & Business Metrics
| Metric | Definition | Goal |
| :--- | :--- | :--- |
| **Reduction in "Nit" PR Comments** | % of PR comments related to verified patterns | **-40%** |
| **Junior Velocity** | Average time to close first 5 tickets for new hires | **-20%** |
| **CLI Intervention Rate** | % of "risky" commands caught and corrected | **>15%** |
| **Pattern Adoption** | % of new code using strict "Golden Path" libraries | **>90%** |