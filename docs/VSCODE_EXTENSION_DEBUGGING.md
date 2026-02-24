# VSCode Extension Debugging (Aura Guardian)

This guide explains how to debug the Aura VSCode extension (`clients/vscode`) in **VSCode** or **Cursor**.

## Prerequisites

- Aura backend running locally (recommended via Docker): `just dev` or `just dev-detached`
- Backend health check reachable at `http://localhost:8000/health`

## Debug from the repo root (recommended)

Aura does not commit editor workspace settings by default (the repo `.gitignore` ignores `.vscode/`).
To debug the extension, create **local** VSCode/Cursor debug configs under `.vscode/` in the repo root.

### 0) Create `.vscode/launch.json` (local)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Aura Guardian: Extension Host",
      "request": "launch",
      "type": "extensionHost",
      "args": [
        "--disable-extensions",
        "--extensionDevelopmentPath=${workspaceFolder}/clients/vscode",
        "${workspaceFolder}"
      ],
      "outFiles": ["${workspaceFolder}/clients/vscode/out/**/*.js"],
      "preLaunchTask": "Aura Guardian: compile"
    },
    {
      "name": "Aura Guardian: Extension Host (watch)",
      "request": "launch",
      "type": "extensionHost",
      "args": [
        "--disable-extensions",
        "--extensionDevelopmentPath=${workspaceFolder}/clients/vscode",
        "${workspaceFolder}"
      ],
      "outFiles": ["${workspaceFolder}/clients/vscode/out/**/*.js"],
      "preLaunchTask": "Aura Guardian: watch"
    }
  ]
}
```

### 0.1) Create `.vscode/tasks.json` (local)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Aura Guardian: compile",
      "type": "shell",
      "command": "npm",
      "args": ["--prefix", "clients/vscode", "run", "compile"],
      "problemMatcher": []
    },
    {
      "label": "Aura Guardian: watch",
      "type": "shell",
      "command": "npm",
      "args": ["--prefix", "clients/vscode", "run", "watch"],
      "isBackground": true,
      "problemMatcher": ["$tsc-watch"]
    }
  ]
}
```

### 1) Build (or watch) the extension

In your editor, open **Run and Debug** and start one of:

- **Aura Guardian: Extension Host** (one-time build)
- **Aura Guardian: Extension Host (watch)** (rebuilds on change)

These will run the corresponding tasks:

- `Aura Guardian: compile` → `npm --prefix clients/vscode run compile`
- `Aura Guardian: watch` → `npm --prefix clients/vscode run watch`

### 2) Configure extension settings (Extension Development Host)

In the Extension Development Host window:

- Set `aura.baseUrl` to your backend (default `http://localhost:8000`)
- Ensure `aura.enabled` is `true`

Privacy controls:

- `aura.sendCodeSnippet` (default `true`)
- `aura.sendFilePath` (default `false`)

### 3) Trigger a struggle signal

You can trigger detection in two ways:

- **Retry edits**: make 3+ similar edits near the same line within the configured window
- **Diagnostics errors**: introduce a real error so VSCode produces `DiagnosticSeverity.Error`

### 4) Verify the UI

When a recommendation is returned from the backend:

- A notification appears (Show lesson / Snooze / Disable)
- CodeLens actions appear near the struggle line (if `aura.showCodeLens` is enabled)
- Hover shows an excerpt near the struggle line (if `aura.showHover` is enabled)
- The **Aura Lessons** sidebar view renders the lesson as plain text

## Window configuration (dev vs prod)

Defaults:

- Development Host: `aura.devWindowSeconds` (default 30s)
- Production/default: `aura.windowMinutes` (default 5m)

## Troubleshooting

### No lessons show up

- Confirm backend is running and `aura.baseUrl` is correct
- Check Extension Host logs: **View → Output → Log (Extension Host)**
- Confirm `aura.enabled` is true and you’re not snoozed

### Build/watch task does not start

Run the commands manually in a terminal:

```bash
npm --prefix clients/vscode install
npm --prefix clients/vscode run watch
```

---

## Debugging V2 Multi-Signal Detection

The extension now uses `StruggleServiceV2` with a multi-signal architecture. Each signal type has its own detector that contributes to an aggregated struggle score.

### Signal Detectors

| Signal          | File                       | What It Detects                             |
| --------------- | -------------------------- | ------------------------------------------- |
| **undoRedo**    | `undo-redo-detector.ts`    | Undo/redo keyboard patterns                 |
| **timePattern** | `time-pattern-detector.ts` | Rapid edits or long pauses                  |
| **terminal**    | `terminal-detector.ts`     | Failed tasks/builds                         |
| **debug**       | `debug-detector.ts`        | Repeated debug sessions                     |
| **semantic**    | `semantic-detector.ts`     | Language-aware issues (disabled by default) |
| **editPattern** | `edit-pattern-detector.ts` | Repeated edits + diagnostics                |

### Add logging to see signal scores

In `struggle-service-v2.ts`, add temporary logging inside `onDocumentChanged()`:

```typescript
const aggregated = this.aggregator.evaluate(fileKey, now);
console.log("[Aura V2] Signals:", JSON.stringify(aggregated.signals));
console.log("[Aura V2] Score:", aggregated.score, "Trigger:", aggregated.shouldTrigger);
```

View logs: **View → Output → Log (Extension Host)**

### Set breakpoints in detectors

1. Open the detector file you want to debug (e.g., `src/signals/edit-pattern-detector.ts`)
2. Set breakpoints in:
   - `recordEdit()` / `recordChange()` – when events are captured
   - `evaluate()` – when scores are computed
3. Start the Extension Host debugger and trigger the signal

### Adjust thresholds at runtime

Lower thresholds for easier testing by calling these in the debug console:

```javascript
// Access the struggle service (from extension.ts context)
struggleService.updateThreshold(0.1); // Lower trigger threshold
struggleService.updateWeights({ editPattern: 2.0 }); // Boost edit weight
```

### Trigger specific signals

| Signal          | How to Trigger                           |
| --------------- | ---------------------------------------- |
| **editPattern** | Make 3+ similar edits near the same line |
| **undoRedo**    | Press Cmd/Ctrl+Z multiple times          |
| **timePattern** | Edit rapidly or pause then resume        |
| **terminal**    | Run a failing build task                 |
| **debug**       | Start/stop debug sessions repeatedly     |
| **semantic**    | Introduce type errors (TypeScript files) |

### Check aggregator config

```javascript
console.log(struggleService.getConfig());
// Shows: { windowMs, triggerThreshold, weights, cooldownMs }
```
