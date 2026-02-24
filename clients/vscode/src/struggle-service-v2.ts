/**
 * Struggle Service V2
 *
 * Enhanced struggle detection using the multi-signal architecture.
 * Replaces the original StruggleService with configurable signal detectors.
 */

import * as vscode from "vscode";
import type { AggregatedStruggle, AggregatorConfig, Clock, SignalType } from "./signals/types";
import { SignalAggregator } from "./signals/signal-aggregator";
import { UndoRedoDetector } from "./signals/undo-redo-detector";
import { TimePatternDetector } from "./signals/time-pattern-detector";
import { TerminalDetector } from "./signals/terminal-detector";
import { DebugDetector } from "./signals/debug-detector";
import { SemanticDetector } from "./signals/semantic-detector";
import { EditPatternDetector } from "./signals/edit-pattern-detector";

/**
 * Configuration for which signals are enabled.
 */
export type SignalEnableConfig = {
  undoRedo: boolean;
  timePattern: boolean;
  terminal: boolean;
  debug: boolean;
  semantic: boolean;
  editPattern: boolean;
};

/**
 * Full configuration for StruggleServiceV2.
 */
export type StruggleServiceV2Config = {
  /** Signal enable flags */
  signals: SignalEnableConfig;
  /** Aggregator configuration */
  aggregator: Partial<AggregatorConfig>;
  /** Window duration in ms */
  windowMs: number;
};

const DEFAULT_SIGNAL_ENABLE: SignalEnableConfig = {
  undoRedo: true,
  timePattern: true,
  terminal: true,
  debug: true,
  semantic: false, // Disabled by default due to overhead
  editPattern: true,
};

/**
 * Context about the detected struggle for backend reporting.
 */
export type StruggleContextV2 = {
  fileKey: string | null;
  filePath: string | null;
  languageId: string | null;
  snippet: string | null;
  line: number | null;
  diagnosticsErrors: string[];
};

/**
 * Combined detection result.
 */
export type StruggleDetectionV2 = {
  aggregated: AggregatedStruggle;
  context: StruggleContextV2;
};

function safeFsPath(uri: vscode.Uri): string | null {
  try {
    return uri.scheme === "file" ? uri.fsPath : null;
  } catch {
    return null;
  }
}

function extractSnippet(doc: vscode.TextDocument, line: number, maxChars: number): string {
  const startLine = Math.max(0, line - 2);
  const endLine = Math.min(doc.lineCount - 1, line + 2);
  const start = new vscode.Position(startLine, 0);
  const end = new vscode.Position(endLine, doc.lineAt(endLine).text.length);
  const snippet = doc.getText(new vscode.Range(start, end));
  return snippet.slice(0, maxChars);
}

/**
 * Enhanced struggle detection service using multi-signal architecture.
 */
export class StruggleServiceV2 {
  private readonly clock: Clock;
  private readonly aggregator: SignalAggregator;
  private readonly enableConfig: SignalEnableConfig;
  private readonly maxSnippetChars: number;

  // Detectors (stored for direct access and event forwarding)
  private readonly undoRedoDetector?: UndoRedoDetector;
  private readonly timePatternDetector?: TimePatternDetector;
  private readonly terminalDetector?: TerminalDetector;
  private readonly debugDetector?: DebugDetector;
  private readonly semanticDetector?: SemanticDetector;
  private readonly editPatternDetector?: EditPatternDetector;

  // Track the last active document for context
  private lastActiveFileKey: string | null = null;
  private lastActiveLine: number | null = null;

  constructor(config: StruggleServiceV2Config, clock?: Clock) {
    this.clock = clock ?? { nowMs: () => Date.now() };
    this.enableConfig = { ...DEFAULT_SIGNAL_ENABLE, ...config.signals };
    this.maxSnippetChars = 300;

    // Create aggregator with provided config
    this.aggregator = new SignalAggregator(
      {
        windowMs: config.windowMs,
        ...config.aggregator,
      },
      this.clock
    );

    // Create and register enabled detectors
    if (this.enableConfig.undoRedo) {
      this.undoRedoDetector = new UndoRedoDetector({ windowMs: config.windowMs }, this.clock);
      this.aggregator.registerDetector(this.undoRedoDetector);
    }

    if (this.enableConfig.timePattern) {
      this.timePatternDetector = new TimePatternDetector({ windowMs: config.windowMs }, this.clock);
      this.aggregator.registerDetector(this.timePatternDetector);
    }

    if (this.enableConfig.terminal) {
      this.terminalDetector = new TerminalDetector({ windowMs: config.windowMs * 2 }, this.clock);
      this.aggregator.registerDetector(this.terminalDetector);
    }

    if (this.enableConfig.debug) {
      this.debugDetector = new DebugDetector({ windowMs: config.windowMs * 2 }, this.clock);
      this.aggregator.registerDetector(this.debugDetector);
    }

    if (this.enableConfig.semantic) {
      this.semanticDetector = new SemanticDetector({ windowMs: config.windowMs }, this.clock);
      this.aggregator.registerDetector(this.semanticDetector);
    }

    if (this.enableConfig.editPattern) {
      this.editPatternDetector = new EditPatternDetector({ windowMs: config.windowMs }, this.clock);
      this.aggregator.registerDetector(this.editPatternDetector);
    }
  }

  /**
   * Subscribe detectors to VSCode events.
   * Returns disposables that should be added to context.subscriptions.
   */
  subscribeToEvents(): vscode.Disposable[] {
    const disposables: vscode.Disposable[] = [];

    if (this.terminalDetector) {
      disposables.push(this.terminalDetector.subscribeToTasks());
    }

    if (this.debugDetector) {
      disposables.push(...this.debugDetector.subscribeToDebug());
    }

    return disposables;
  }

  /**
   * Process a document change event.
   * Returns a detection result if struggle should trigger, null otherwise.
   */
  onDocumentChanged(event: vscode.TextDocumentChangeEvent): StruggleDetectionV2 | null {
    const doc = event.document;
    if (doc.uri.scheme !== "file") return null;
    if (event.contentChanges.length === 0) return null;

    const now = this.clock.nowMs();
    const fileKey = doc.uri.toString();
    const primaryLine = event.contentChanges[0]?.range?.start?.line ?? 0;

    // Update tracking
    this.lastActiveFileKey = fileKey;
    this.lastActiveLine = primaryLine;

    // Forward to detectors
    this.undoRedoDetector?.recordChange(event);
    this.timePatternDetector?.recordEdit(fileKey, now);
    this.editPatternDetector?.recordEdit(event, now);
    this.semanticDetector?.scheduleAnalysis(doc);

    // Evaluate aggregated signals
    const aggregated = this.aggregator.evaluate(fileKey, now);

    if (!aggregated.shouldTrigger) return null;

    // Build context
    const snippet = extractSnippet(doc, primaryLine, this.maxSnippetChars);
    const diagnosticsErrors = this.editPatternDetector?.getErrors(fileKey) ?? [];

    return {
      aggregated,
      context: {
        fileKey,
        filePath: safeFsPath(doc.uri),
        languageId: doc.languageId ?? null,
        snippet,
        line: primaryLine,
        diagnosticsErrors,
      },
    };
  }

  /**
   * Process a diagnostics change event.
   */
  onDiagnosticsChanged(e: vscode.DiagnosticChangeEvent): void {
    this.editPatternDetector?.onDiagnosticsChanged(e);
  }

  /**
   * Manually trigger evaluation for the current file.
   * Useful for testing or explicit evaluation requests.
   */
  evaluate(fileKey?: string): AggregatedStruggle {
    const key = fileKey ?? this.lastActiveFileKey;
    return this.aggregator.evaluate(key);
  }

  /**
   * Update aggregator weights at runtime.
   */
  updateWeights(weights: Partial<Record<SignalType, number>>): void {
    const currentConfig = this.aggregator.getConfig();
    const mergedWeights = { ...currentConfig.weights, ...weights };
    this.aggregator.updateConfig({ weights: mergedWeights });
  }

  /**
   * Update trigger threshold at runtime.
   */
  updateThreshold(threshold: number): void {
    this.aggregator.updateConfig({ triggerThreshold: threshold });
  }

  /**
   * Get current aggregator configuration.
   */
  getConfig(): ReturnType<SignalAggregator["getConfig"]> {
    return this.aggregator.getConfig();
  }

  /**
   * Reset state for a specific file or all files.
   */
  reset(fileKey: string | null = null): void {
    this.aggregator.reset(fileKey);
    if (!fileKey) {
      this.lastActiveFileKey = null;
      this.lastActiveLine = null;
    }
  }

  /**
   * Dispose all detectors and resources.
   */
  dispose(): void {
    this.aggregator.dispose();
    this.lastActiveFileKey = null;
    this.lastActiveLine = null;
  }
}
