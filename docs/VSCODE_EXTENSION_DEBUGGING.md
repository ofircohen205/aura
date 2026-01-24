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
