# Story: Build VSCode Extension Host Logic

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
- **Architecture**: Follow `docs/workflows/project-architecture.md` (VSCode Extension Architecture section).
- **New Features**: Follow `docs/workflows/common-tasks.md`.

### Implementation Checklist
- [ ] Initialize VSCode extension project (`yo code`).
- [ ] Implement `activate()` context subscription.
- [ ] Create `StruggleService` to buffer edit events.
- [ ] Implement connection to Python Backend (check health on startup).
- [ ] Create `LessonPanel` (Webview) to render HTML/Markdown responses.

## Testing Plan
- **Automated Tests**:
    - [ ] VSCode Extension Tests (`@vscode/test-electron`).
    - [ ] Unit tests for `StruggleService` logic (jest).
- **Manual Verification**:
    - [ ] F5 (Run Extension) -> "Hello World".
    - [ ] Simulate rapid typing and verify console logs trigger "Struggle Detected" candidates.
