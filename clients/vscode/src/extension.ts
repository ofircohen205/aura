import * as vscode from "vscode";
import { StruggleService } from "./struggle-service";
import { BackendClient } from "./backend-client";
import { LessonPanel } from "./lesson-panel";

type LessonState = {
  uri: vscode.Uri;
  fileKey: string;
  lesson: string;
  line: number;
  reason: string | null;
  createdAtMs: number;
};

const COMMAND_SHOW_LESSON = "aura.showLesson";
const COMMAND_DISMISS_LESSON = "aura.dismissLesson";

export function activate(context: vscode.ExtensionContext) {
  console.log("Aura Guardian is now active!");

  const auraCfg = vscode.workspace.getConfiguration("aura");

  const windowMinutes = auraCfg.get<number>("windowMinutes", 5);
  const devWindowSeconds = auraCfg.get<number>("devWindowSeconds", 30);
  const retryAttemptThreshold = auraCfg.get<number>("retryAttemptThreshold", 3);
  const cooldownMinutes = auraCfg.get<number>("cooldownMinutes", 2);
  const maxSnippetChars = auraCfg.get<number>("maxSnippetChars", 300);

  const windowMs =
    context.extensionMode === vscode.ExtensionMode.Development
      ? Math.max(5, devWindowSeconds) * 1000
      : Math.max(0.1, windowMinutes) * 60_000;

  const backendClient = new BackendClient();
  const struggleService = new StruggleService({
    windowMs,
    retryAttemptThreshold,
    cooldownMs: Math.max(0, cooldownMinutes) * 60_000,
    maxSnippetChars,
  });
  const lessonPanel = new LessonPanel();

  const lessonsByFileKey = new Map<string, LessonState>();
  const codeLensRefresh = new vscode.EventEmitter<void>();

  // Register Webview
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(LessonPanel.viewType, lessonPanel)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(COMMAND_SHOW_LESSON, (uri?: vscode.Uri) => {
      const targetUri = uri ?? vscode.window.activeTextEditor?.document.uri;
      if (!targetUri) return;
      const fileKey = targetUri.toString();
      const state = lessonsByFileKey.get(fileKey);
      if (!state) return;

      void vscode.commands.executeCommand("workbench.view.extension.aura-sidebar");
      lessonPanel.showLesson(state.lesson);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(COMMAND_DISMISS_LESSON, (uri?: vscode.Uri) => {
      const targetUri = uri ?? vscode.window.activeTextEditor?.document.uri;
      if (!targetUri) return;
      lessonsByFileKey.delete(targetUri.toString());
      codeLensRefresh.fire();
    })
  );

  // CodeLens to expose the latest lesson contextually
  if (auraCfg.get<boolean>("showCodeLens", true)) {
    context.subscriptions.push(
      vscode.languages.registerCodeLensProvider(
        { scheme: "file" },
        {
          onDidChangeCodeLenses: codeLensRefresh.event,
          provideCodeLenses: document => {
            const state = lessonsByFileKey.get(document.uri.toString());
            if (!state) return [];

            const range = new vscode.Range(state.line, 0, state.line, 0);
            return [
              new vscode.CodeLens(range, {
                title: "Aura: Show lesson",
                command: COMMAND_SHOW_LESSON,
                arguments: [document.uri],
              }),
              new vscode.CodeLens(range, {
                title: "Aura: Dismiss",
                command: COMMAND_DISMISS_LESSON,
                arguments: [document.uri],
              }),
            ];
          },
        }
      )
    );
  }

  // Hover to show a short excerpt near the struggle location
  if (auraCfg.get<boolean>("showHover", true)) {
    context.subscriptions.push(
      vscode.languages.registerHoverProvider(
        { scheme: "file" },
        {
          provideHover: (document, position) => {
            const state = lessonsByFileKey.get(document.uri.toString());
            if (!state) return null;
            if (Math.abs(position.line - state.line) > 2) return null;

            const excerpt =
              state.lesson.length > 500 ? `${state.lesson.slice(0, 500)}…` : state.lesson;
            const md = new vscode.MarkdownString();
            md.appendMarkdown("**Aura suggestion**\n\n");
            md.appendCodeblock(excerpt);
            md.isTrusted = false;

            const range = new vscode.Range(state.line, 0, state.line, 0);
            return new vscode.Hover(md, range);
          },
        }
      )
    );
  }

  // Register Document Change Listener
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(event => {
      const enabled = vscode.workspace.getConfiguration("aura").get<boolean>("enabled", true);
      if (!enabled) return;
      const snoozedUntilMs = context.globalState.get<number>("aura.snoozedUntilMs", 0);
      if (Date.now() < snoozedUntilMs) return;

      const detection = struggleService.onDocumentChanged(event);
      if (!detection) return;

      const { decision, context: struggleContext } = detection;

      const cfg = vscode.workspace.getConfiguration("aura");
      const sendCodeSnippet = cfg.get<boolean>("sendCodeSnippet", true);
      const sendFilePath = cfg.get<boolean>("sendFilePath", false);

      // Trigger backend workflow; UI surfacing happens in a follow-up step.
      void backendClient
        .triggerStruggleWorkflow({
          edit_frequency: decision.metrics.editFrequencyPerMin,
          error_logs: struggleContext.diagnosticsErrors,
          history: sendCodeSnippet && struggleContext.snippet ? [struggleContext.snippet] : [],
          source: "vscode",
          file_path: sendFilePath ? struggleContext.filePath : null,
          language_id: struggleContext.languageId,
          code_snippet: sendCodeSnippet ? struggleContext.snippet : null,
          client_timestamp: Date.now(),
          struggle_reason: decision.reason,
          retry_count: decision.metrics.retryCount,
        })
        .then(result => {
          if (!result) return;
          const state = (result.state ?? {}) as Record<string, unknown>;
          const isStruggling = state["is_struggling"] === true;
          const lesson =
            typeof state["lesson_recommendation"] === "string"
              ? (state["lesson_recommendation"] as string)
              : null;

          if (!isStruggling || !lesson) return;

          const uri = event.document.uri;
          const fileKey = uri.toString();
          const line = struggleContext.line ?? 0;
          lessonsByFileKey.set(fileKey, {
            uri,
            fileKey,
            lesson,
            line,
            reason: decision.reason,
            createdAtMs: Date.now(),
          });
          codeLensRefresh.fire();

          void vscode.window
            .showInformationMessage(
              "Aura: It looks like you might be stuck. Want a lesson recommendation?",
              "Show lesson",
              "Snooze 10m",
              "Disable"
            )
            .then(selection => {
              if (selection === "Show lesson") {
                void vscode.commands.executeCommand(COMMAND_SHOW_LESSON, uri);
                return;
              }

              if (selection === "Snooze 10m") {
                const snoozeUntil = Date.now() + 10 * 60_000;
                void context.globalState.update("aura.snoozedUntilMs", snoozeUntil);
                return;
              }

              if (selection === "Disable") {
                void vscode.workspace
                  .getConfiguration("aura")
                  .update("enabled", false, vscode.ConfigurationTarget.Global);
                return;
              }
            });
        });
    })
  );

  // Register diagnostics listener to capture compilation/type errors
  context.subscriptions.push(
    vscode.languages.onDidChangeDiagnostics(e => {
      struggleService.onDiagnosticsChanged(e);
    })
  );

  // Initial Health Check
  backendClient.healthCheck().then(healthy => {
    if (healthy) {
      console.log("Connected to Aura Backend");
    } else {
      console.log("Could not connect to Aura Backend");
    }
  });
}

export function deactivate() {}
