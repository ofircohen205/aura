import * as vscode from "vscode";

export class LessonPanel implements vscode.WebviewViewProvider {
  public static readonly viewType = "aura.lessonPanel";
  private _view?: vscode.WebviewView;
  private pendingContent: string | null = null;

  constructor() {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    if (this.pendingContent) {
      this._view.webview.postMessage({ type: "showLesson", content: this.pendingContent });
      this.pendingContent = null;
    }
  }

  public showLesson(content: string) {
    if (this._view) {
      this._view.webview.postMessage({ type: "showLesson", content: content });
    } else {
      this.pendingContent = content;
    }
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>Aura Lessons</title>
                <style>
                    body { font-family: var(--vscode-font-family); padding: 10px; }
                    .lesson-card { background: var(--vscode-editor-background); border: 1px solid var(--vscode-widget-border); padding: 10px; margin-bottom: 10px; }
                </style>
			</head>
			<body>
				<div class="lesson-card">
                    <h3>Aura Lessons</h3>
                    <p id="status">Start coding to receive guidance.</p>
                    <pre id="content" style="white-space: pre-wrap; margin-top: 10px;"></pre>
                </div>
                <script>
                    const vscode = acquireVsCodeApi();
                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'showLesson':
                                // Treat all content as untrusted; render as plain text.
                                document.getElementById('status').textContent = "Lesson recommendation:";
                                document.getElementById('content').textContent = String(message.content ?? "");
                                break;
                        }
                    });
                </script>
			</body>
			</html>`;
  }
}
