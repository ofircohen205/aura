/**
 * Undo/Redo Detector
 *
 * Detects struggle patterns based on undo/redo operations.
 * Uses VSCode's TextDocumentChangeReason to identify undo/redo events.
 */

import * as vscode from "vscode";
import type { Clock, SignalDetector, SignalEvent } from "./types";

type UndoRedoEvent = {
  tsMs: number;
  fileKey: string;
  type: "undo" | "redo";
};

export type UndoRedoDetectorConfig = {
  /** Time window for tracking undo/redo events in ms */
  windowMs: number;
  /** Minimum undo count to generate a signal */
  minUndoCount: number;
  /** Undo-redo-undo cycle detection threshold */
  cycleThreshold: number;
  /** Maximum events to track per file */
  maxEventsPerFile: number;
};

const DEFAULT_CONFIG: UndoRedoDetectorConfig = {
  windowMs: 60_000, // 1 minute
  minUndoCount: 3,
  cycleThreshold: 2, // At least 2 undo-redo cycles
  maxEventsPerFile: 100,
};

/**
 * Detects undo/redo patterns that may indicate struggle.
 *
 * Patterns detected:
 * - High undo frequency (trying different approaches)
 * - Undo-redo-undo cycling (uncertainty about changes)
 */
export class UndoRedoDetector implements SignalDetector {
  public readonly type = "undo_redo" as const;

  private readonly clock: Clock;
  private readonly config: UndoRedoDetectorConfig;
  private readonly eventsByFile: Map<string, UndoRedoEvent[]> = new Map();

  constructor(config?: Partial<UndoRedoDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Record a document change event, extracting undo/redo information.
   * Call this from onDidChangeTextDocument handler.
   */
  recordChange(event: vscode.TextDocumentChangeEvent): void {
    // TextDocumentChangeReason is available in VSCode 1.44+
    // 1 = Undo, 2 = Redo
    const reason = event.reason;
    if (
      reason !== vscode.TextDocumentChangeReason.Undo &&
      reason !== vscode.TextDocumentChangeReason.Redo
    ) {
      return;
    }

    const now = this.clock.nowMs();
    const fileKey = event.document.uri.toString();
    const type = reason === vscode.TextDocumentChangeReason.Undo ? "undo" : "redo";

    const events = this.getOrCreateEvents(fileKey);
    events.push({ tsMs: now, fileKey, type });

    // Prune old events and limit size
    this.pruneEvents(fileKey, now);
  }

  /**
   * Evaluate the current undo/redo patterns for a file.
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();
    const signals: SignalEvent[] = [];

    if (fileKey) {
      const signal = this.evaluateFile(fileKey, now);
      if (signal) signals.push(signal);
    } else {
      // Evaluate all tracked files
      for (const key of this.eventsByFile.keys()) {
        const signal = this.evaluateFile(key, now);
        if (signal) signals.push(signal);
      }
    }

    return signals;
  }

  private evaluateFile(fileKey: string, now: number): SignalEvent | null {
    const events = this.eventsByFile.get(fileKey);
    if (!events || events.length === 0) return null;

    // Prune to window
    const windowStart = now - this.config.windowMs;
    const windowEvents = events.filter(e => e.tsMs >= windowStart);
    if (windowEvents.length === 0) return null;

    // Count undos and redos
    const undoCount = windowEvents.filter(e => e.type === "undo").length;
    const redoCount = windowEvents.filter(e => e.type === "redo").length;

    // Detect undo-redo cycles
    const cycleCount = this.detectCycles(windowEvents);

    // Calculate score based on patterns
    let score = 0;
    let pattern: string | undefined;

    // High undo count indicates trying different approaches
    if (undoCount >= this.config.minUndoCount) {
      score = Math.min(1, undoCount / (this.config.minUndoCount * 2));
      pattern = `${undoCount} undos in window`;
    }

    // Undo-redo cycling is a stronger signal
    if (cycleCount >= this.config.cycleThreshold) {
      const cycleScore = Math.min(1, cycleCount / (this.config.cycleThreshold * 2));
      if (cycleScore > score) {
        score = cycleScore;
        pattern = `${cycleCount} undo-redo cycles detected`;
      }
    }

    // No significant pattern detected
    if (score === 0) return null;

    return {
      type: "undo_redo",
      score,
      tsMs: now,
      fileKey,
      metadata: {
        pattern,
        undoCount,
        redoCount,
      },
    };
  }

  /**
   * Detect undo-redo-undo cycling patterns.
   * A cycle is: undo -> redo -> undo (or redo -> undo -> redo)
   */
  private detectCycles(events: UndoRedoEvent[]): number {
    if (events.length < 3) return 0;

    let cycles = 0;
    for (let i = 0; i < events.length - 2; i++) {
      const a = events[i].type;
      const b = events[i + 1].type;
      const c = events[i + 2].type;

      // undo -> redo -> undo or redo -> undo -> redo
      if (a !== b && b !== c && a === c) {
        cycles++;
        i++; // Skip one to avoid double-counting overlapping cycles
      }
    }

    return cycles;
  }

  private getOrCreateEvents(fileKey: string): UndoRedoEvent[] {
    let events = this.eventsByFile.get(fileKey);
    if (!events) {
      events = [];
      this.eventsByFile.set(fileKey, events);
    }
    return events;
  }

  private pruneEvents(fileKey: string, now: number): void {
    const events = this.eventsByFile.get(fileKey);
    if (!events) return;

    const windowStart = now - this.config.windowMs;

    // Remove events outside window
    let idx = 0;
    while (idx < events.length && events[idx].tsMs < windowStart) idx++;
    if (idx > 0) events.splice(0, idx);

    // Limit size
    if (events.length > this.config.maxEventsPerFile) {
      events.splice(0, events.length - this.config.maxEventsPerFile);
    }
  }

  reset(fileKey: string | null): void {
    if (fileKey) {
      this.eventsByFile.delete(fileKey);
    } else {
      this.eventsByFile.clear();
    }
  }

  dispose(): void {
    this.eventsByFile.clear();
  }
}
