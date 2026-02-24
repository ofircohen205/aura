import * as vscode from "vscode";
import { StruggleServiceV2 } from "./struggle-service-v2";
import { BackendClient } from "./backend-client";
import { LessonPanel } from "./lesson-panel";
import type { SignalWeights } from "./signals/types";

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

  // Window configuration
  const windowMinutes = auraCfg.get<number>("windowMinutes", 5);
  const devWindowSeconds = auraCfg.get<number>("devWindowSeconds", 30);
  const cooldownMinutes = auraCfg.get<number>("cooldownMinutes", 2);

  const windowMs =
    context.extensionMode === vscode.ExtensionMode.Development
      ? Math.max(5, devWindowSeconds) * 1000
      : Math.max(0.1, windowMinutes) * 60_000;

  // Signal enable configuration
  const signalConfig = {
    undoRedo: auraCfg.get<boolean>("signals.undoRedo.enabled", true),
    timePattern: auraCfg.get<boolean>("signals.timePattern.enabled", true),
    terminal: auraCfg.get<boolean>("signals.terminal.enabled", true),
    debug: auraCfg.get<boolean>("signals.debug.enabled", true),
    semantic: auraCfg.get<boolean>("signals.semantic.enabled", false),
    editPattern: auraCfg.get<boolean>("signals.editPattern.enabled", true),
  };

  // Aggregation configuration
  const triggerThreshold = auraCfg.get<number>("aggregation.triggerThreshold", 0.6);
  const weights: SignalWeights = {
    undo_redo: auraCfg.get<number>("aggregation.weights.undoRedo", 0.25),
    time_pattern: auraCfg.get<number>("aggregation.weights.timePattern", 0.2),
    terminal: auraCfg.get<number>("aggregation.weights.terminal", 0.2),
    debug: auraCfg.get<number>("aggregation.weights.debug", 0.15),
    semantic: auraCfg.get<number>("aggregation.weights.semantic", 0.1),
    edit_pattern: auraCfg.get<number>("aggregation.weights.editPattern", 0.1),
  };

  const backendClient = new BackendClient();
  const struggleService = new StruggleServiceV2({
    signals: signalConfig,
    windowMs,
    aggregator: {
      triggerThreshold,
      weights,
      cooldownMs: Math.max(0, cooldownMinutes) * 60_000,
      windowMs,
    },
  });

  // Subscribe detectors to VSCode events
  const eventSubscriptions = struggleService.subscribeToEvents();
  context.subscriptions.push(...eventSubscriptions);

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

      const { aggregated, context: struggleContext } = detection;

      const cfg = vscode.workspace.getConfiguration("aura");
      const sendCodeSnippet = cfg.get<boolean>("sendCodeSnippet", true);
      const sendFilePath = cfg.get<boolean>("sendFilePath", false);

      // Build enhanced payload with signal information
      const signalMetadata = aggregated.signals.map(s => ({
        type: s.type,
        score: s.score,
        metadata: s.metadata,
      }));

      // Trigger backend workflow with enhanced signal data
      void backendClient
        .triggerStruggleWorkflow({
          edit_frequency:
            aggregated.signals.find(s => s.type === "edit_pattern")?.metadata.editFrequencyPerMin ??
            0,
          error_logs: struggleContext.diagnosticsErrors,
          history: sendCodeSnippet && struggleContext.snippet ? [struggleContext.snippet] : [],
          source: "vscode",
          file_path: sendFilePath ? struggleContext.filePath : null,
          language_id: struggleContext.languageId,
          code_snippet: sendCodeSnippet ? struggleContext.snippet : null,
          client_timestamp: Date.now(),
          struggle_reason: aggregated.primarySignal,
          retry_count:
            aggregated.signals.find(s => s.type === "edit_pattern")?.metadata.retryCount ?? 0,
          // Enhanced signal fields
          combined_score: aggregated.combinedScore,
          primary_signal: aggregated.primarySignal,
          signals: signalMetadata,
          undo_redo_pattern:
            aggregated.signals.find(s => s.type === "undo_redo")?.metadata.pattern ?? null,
          hesitation_ms:
            aggregated.signals.find(s => s.type === "time_pattern")?.metadata.hesitationMs ?? null,
          terminal_errors:
            aggregated.signals.find(s => s.type === "terminal")?.metadata.terminalErrors ?? null,
          debug_breakpoint_changes:
            aggregated.signals.find(s => s.type === "debug")?.metadata.breakpointChanges ?? null,
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
            reason: aggregated.primarySignal,
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

  // Cleanup on deactivation
  context.subscriptions.push({
    dispose: () => {
      struggleService.dispose();
    },
  });

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
