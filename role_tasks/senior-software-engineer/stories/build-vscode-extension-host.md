# Story: Build VSCode Extension Host Logic

**GitHub Issue**: #4

**Role:** Senior Software Engineer
**Related SRS Section:** 1, 2.2, 3.1, 4.2

## Desired Feature

The VSCode extension needs a robust "Host" process that can communicate with the VSCode API, track document changes, and interface with the Aura Backend. It acts as the "eyes and ears" tailored for the IDE context.

## Planning & Technical Spec

### Architecture

- **Language**: TypeScript (Node.js/Electron context).
- **Communication**: HTTP/WebSocket to Backend (`localhost:8000`).
- **Components**:
  - `DocumentTracker`: Listens to `vscode.workspace.onDidChangeTextDocument`.
  - `StruggleDetector`: Local lightweight analysis (debounce edits, calculate edit distance).
  - `LessonRenderer`: WebView provider to show content.
  - `StatusBarItem`: Shows Aura status.

### Standards & Workflows

- **Git Flow**: Create a new branch for this story and work only on that branch.
- **Issue Updates**: Reference the GitHub Issue (check header) in your commits and PRs.
- **Architecture**: Follow `docs/workflows/project-architecture.md` (VSCode Extension Architecture section).
- **New Features**: Follow `docs/workflows/common-tasks.md`.

### Implementation Checklist

- [x] Initialize VSCode extension project (`yo code`).
- [x] Implement `activate()` context subscription.
- [x] Create `StruggleService` to buffer edit events.
- [x] Implement connection to Python Backend (check health on startup).
- [x] Create `LessonPanel` (Webview) to render HTML/Markdown responses.

## Testing Plan

- **Automated Tests**:
  - [x] VSCode Extension Tests (`@vscode/test-electron`).
  - [x] Unit tests for `StruggleService` logic (jest).
- **Manual Verification**:
  - [x] F5 (Run Extension) -> "Hello World".
  - [x] Simulate rapid typing and verify console logs trigger "Struggle Detected" candidates.
