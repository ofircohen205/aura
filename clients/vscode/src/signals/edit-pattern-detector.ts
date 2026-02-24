/**
 * Edit Pattern Detector
 *
 * Refactored from the original StruggleDetector.
 * Uses Levenshtein distance for retry detection and tracks edit patterns.
 *
 * This detector maintains the legacy behavior with lower weight in the new system.
 */

import * as vscode from "vscode";
import type { Clock, SignalDetector, SignalEvent } from "./types";

type EditEvent = {
  tsMs: number;
  fileKey: string;
  snippet: string;
  line: number;
};

type ErrorEvent = {
  tsMs: number;
  fileKey: string;
  message: string;
};

type FileState = {
  edits: EditEvent[];
  errors: ErrorEvent[];
};

export type EditPatternDetectorConfig = {
  /** Time window for tracking edits in ms */
  windowMs: number;
  /** Number of similar attempts required to trigger retry signal */
  retryAttemptThreshold: number;
  /** Error count threshold */
  errorCountThreshold: number;
  /** Edit frequency threshold per minute */
  editFrequencyThresholdPerMin: number;
  /** Maximum characters in snippet */
  maxSnippetChars: number;
  /** Maximum events to track per file */
  maxEventsPerFile: number;
  /** Maximum errors to track per file */
  maxErrorsPerFile: number;
  /** Levenshtein similarity threshold (0-1, lower = more similar) */
  levenshteinSimilarityThreshold: number;
  /** Maximum edits to compare for retry detection */
  maxComparisonsPerEdit: number;
  /** Maximum line distance for retry comparison */
  maxLineDistanceForRetry: number;
};

const DEFAULT_CONFIG: EditPatternDetectorConfig = {
  windowMs: 5 * 60_000, // 5 minutes
  retryAttemptThreshold: 3,
  errorCountThreshold: 2,
  editFrequencyThresholdPerMin: 10,
  maxSnippetChars: 300,
  maxEventsPerFile: 200,
  maxErrorsPerFile: 20,
  levenshteinSimilarityThreshold: 0.2,
  maxComparisonsPerEdit: 10,
  maxLineDistanceForRetry: 2,
};

/**
 * Calculate Levenshtein distance between two strings.
 * O(min(a,b)) memory DP implementation.
 */
export function levenshteinDistance(a: string, b: string): number {
  if (a === b) return 0;
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  const n = a.length;
  const m = b.length;

  let prev = new Array<number>(m + 1);
  let curr = new Array<number>(m + 1);

  for (let j = 0; j <= m; j++) prev[j] = j;

  for (let i = 1; i <= n; i++) {
    curr[0] = i;
    const ai = a.charCodeAt(i - 1);
    for (let j = 1; j <= m; j++) {
      const cost = ai === b.charCodeAt(j - 1) ? 0 : 1;
      const del = prev[j] + 1;
      const ins = curr[j - 1] + 1;
      const sub = prev[j - 1] + cost;
      curr[j] = Math.min(del, ins, sub);
    }
    const tmp = prev;
    prev = curr;
    curr = tmp;
  }

  return prev[m];
}

function normalizeForComparison(input: string, maxChars: number): string {
  const trimmed = input.trim().slice(0, maxChars);
  return trimmed.replace(/\s+/g, " ");
}

function normalizedDistance(a: string, b: string, maxChars: number): number {
  const na = normalizeForComparison(a, maxChars);
  const nb = normalizeForComparison(b, maxChars);
  const maxLen = Math.max(na.length, nb.length);
  if (maxLen === 0) return 0;
  return levenshteinDistance(na, nb) / maxLen;
}

function pruneToWindow<T extends { tsMs: number }>(items: T[], windowStartMs: number): T[] {
  let idx = 0;
  while (idx < items.length && items[idx].tsMs < windowStartMs) idx++;
  return idx === 0 ? items : items.slice(idx);
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
 * Detects edit-based patterns that may indicate struggle.
 *
 * Patterns detected (legacy):
 * - Retry attempts: Similar edits based on Levenshtein distance
 * - High error count: Many diagnostic errors
 * - High edit frequency: Rapid editing
 */
export class EditPatternDetector implements SignalDetector {
  public readonly type = "edit_pattern" as const;

  private readonly clock: Clock;
  private readonly config: EditPatternDetectorConfig;
  private readonly byFile: Map<string, FileState> = new Map();

  constructor(config?: Partial<EditPatternDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Record an edit event from a document change.
   */
  recordEdit(event: vscode.TextDocumentChangeEvent, tsMs?: number): void {
    const doc = event.document;
    if (doc.uri.scheme !== "file") return;
    if (event.contentChanges.length === 0) return;

    const now = tsMs ?? this.clock.nowMs();
    const fileKey = doc.uri.toString();
    const primaryLine = event.contentChanges[0]?.range?.start?.line ?? 0;
    const snippet = extractSnippet(doc, primaryLine, this.config.maxSnippetChars);

    const state = this.getOrCreateState(fileKey);
    state.edits.push({
      tsMs: now,
      fileKey,
      snippet,
      line: primaryLine,
    });

    const windowStart = now - this.config.windowMs;
    state.edits = pruneToWindow(state.edits, windowStart);
    if (state.edits.length > this.config.maxEventsPerFile) {
      state.edits = state.edits.slice(-this.config.maxEventsPerFile);
    }
  }

  /**
   * Update errors for a file from diagnostics.
   */
  replaceErrors(fileKey: string, messages: string[], tsMs?: number): void {
    const now = tsMs ?? this.clock.nowMs();
    const state = this.getOrCreateState(fileKey);

    const unique = Array.from(new Set(messages))
      .map(m => m.trim())
      .filter(m => m.length > 0)
      .slice(0, this.config.maxErrorsPerFile);

    state.errors = unique.map(message => ({
      tsMs: now,
      fileKey,
      message,
    }));

    const windowStart = now - this.config.windowMs;
    state.errors = pruneToWindow(state.errors, windowStart);
  }

  /**
   * Process a diagnostics change event.
   */
  onDiagnosticsChanged(e: vscode.DiagnosticChangeEvent, tsMs?: number): void {
    const now = tsMs ?? this.clock.nowMs();
    for (const uri of e.uris) {
      if (uri.scheme !== "file") continue;
      const diags = vscode.languages.getDiagnostics(uri);
      const errors = diags
        .filter(d => d.severity === vscode.DiagnosticSeverity.Error)
        .map(d => d.message)
        .filter(m => m && m.trim().length > 0);

      const fileKey = uri.toString();
      this.replaceErrors(fileKey, errors, now);
    }
  }

  /**
   * Evaluate the current edit patterns for a file.
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();
    const signals: SignalEvent[] = [];

    if (fileKey) {
      const signal = this.evaluateFile(fileKey, now);
      if (signal) signals.push(signal);
    } else {
      for (const key of this.byFile.keys()) {
        const signal = this.evaluateFile(key, now);
        if (signal) signals.push(signal);
      }
    }

    return signals;
  }

  private evaluateFile(fileKey: string, now: number): SignalEvent | null {
    const state = this.byFile.get(fileKey);
    if (!state) return null;

    const windowStart = now - this.config.windowMs;
    state.edits = pruneToWindow(state.edits, windowStart);
    state.errors = pruneToWindow(state.errors, windowStart);

    const editCount = state.edits.length;
    const windowMinutes = this.config.windowMs / 60_000;
    const editFrequencyPerMin = windowMinutes > 0 ? editCount / windowMinutes : 0;

    const errorCount = state.errors.length;
    const retryAttemptCount = this.computeRetryAttemptCount(state);
    const retryCount = Math.max(0, retryAttemptCount - 1);

    // Calculate score based on detected patterns
    let score = 0;
    let primaryReason: string | undefined;

    // Retry detection (strongest signal)
    if (retryAttemptCount >= this.config.retryAttemptThreshold) {
      const retryScore = Math.min(1, retryAttemptCount / (this.config.retryAttemptThreshold * 2));
      if (retryScore > score) {
        score = retryScore;
        primaryReason = "retries";
      }
    }

    // Error count
    if (errorCount >= this.config.errorCountThreshold) {
      const errorScore = Math.min(1, errorCount / (this.config.errorCountThreshold * 3));
      if (errorScore > score) {
        score = errorScore;
        primaryReason = "errors";
      }
    }

    // Edit frequency
    if (editFrequencyPerMin >= this.config.editFrequencyThresholdPerMin) {
      const freqScore = Math.min(
        1,
        editFrequencyPerMin / (this.config.editFrequencyThresholdPerMin * 2)
      );
      if (freqScore > score) {
        score = freqScore;
        primaryReason = "frequency";
      }
    }

    if (score === 0) return null;

    return {
      type: "edit_pattern",
      score,
      tsMs: now,
      fileKey,
      metadata: {
        retryCount,
        editFrequencyPerMin,
        errorCount,
        pattern: primaryReason,
      },
    };
  }

  private computeRetryAttemptCount(state: FileState): number {
    const edits = state.edits;
    if (edits.length === 0) return 0;

    const last = edits[edits.length - 1];
    const comparisons = edits.slice(
      Math.max(0, edits.length - 1 - this.config.maxComparisonsPerEdit),
      edits.length - 1
    );

    let similarCount = 0;
    for (const prev of comparisons) {
      if (Math.abs(prev.line - last.line) > this.config.maxLineDistanceForRetry) continue;
      const dist = normalizedDistance(prev.snippet, last.snippet, this.config.maxSnippetChars);
      if (dist <= this.config.levenshteinSimilarityThreshold) {
        similarCount++;
      }
    }

    return 1 + similarCount;
  }

  private getOrCreateState(fileKey: string): FileState {
    const existing = this.byFile.get(fileKey);
    if (existing) return existing;

    const created: FileState = { edits: [], errors: [] };
    this.byFile.set(fileKey, created);
    return created;
  }

  /**
   * Get the current errors for a file (for context building).
   */
  getErrors(fileKey: string): string[] {
    const state = this.byFile.get(fileKey);
    return state?.errors.map(e => e.message) ?? [];
  }

  reset(fileKey: string | null): void {
    if (fileKey) {
      this.byFile.delete(fileKey);
    } else {
      this.byFile.clear();
    }
  }

  dispose(): void {
    this.byFile.clear();
  }
}
