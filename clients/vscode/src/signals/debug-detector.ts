/**
 * Debug Detector
 *
 * Detects struggle signals from debug session behavior.
 * Monitors breakpoint thrashing and short debug sessions.
 */

import * as vscode from "vscode";
import type { Clock, SignalDetector, SignalEvent } from "./types";

type BreakpointEvent = {
  tsMs: number;
  type: "added" | "removed" | "changed";
  count: number;
};

type DebugSessionEvent = {
  tsMs: number;
  sessionId: string;
  startTsMs: number;
  endTsMs: number;
  durationMs: number;
};

export type DebugDetectorConfig = {
  /** Time window for tracking debug events in ms */
  windowMs: number;
  /** Minimum breakpoint changes to generate a signal */
  minBreakpointChanges: number;
  /** Threshold for "short" debug session in ms */
  shortSessionThresholdMs: number;
  /** Minimum short sessions to generate a signal */
  minShortSessions: number;
  /** Maximum events to track */
  maxEvents: number;
};

const DEFAULT_CONFIG: DebugDetectorConfig = {
  windowMs: 10 * 60_000, // 10 minutes
  minBreakpointChanges: 5,
  shortSessionThresholdMs: 30_000, // 30 seconds
  minShortSessions: 2,
  maxEvents: 100,
};

/**
 * Detects debug-related patterns that may indicate struggle.
 *
 * Patterns detected:
 * - Breakpoint thrashing (rapid add/remove)
 * - Short debug sessions (< 30 sec)
 */
export class DebugDetector implements SignalDetector {
  public readonly type = "debug" as const;

  private readonly clock: Clock;
  private readonly config: DebugDetectorConfig;
  private readonly breakpointEvents: BreakpointEvent[] = [];
  private readonly sessionEvents: DebugSessionEvent[] = [];
  private readonly activeSessions: Map<string, number> = new Map(); // sessionId -> startTsMs
  private readonly disposables: vscode.Disposable[] = [];

  constructor(config?: Partial<DebugDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Subscribe to VSCode debug events.
   * Call this during extension activation.
   */
  subscribeToDebug(): vscode.Disposable[] {
    const breakpointDisposable = vscode.debug.onDidChangeBreakpoints(e => {
      this.recordBreakpointChange(e);
    });

    const sessionStartDisposable = vscode.debug.onDidStartDebugSession(session => {
      this.recordSessionStart(session);
    });

    const sessionEndDisposable = vscode.debug.onDidTerminateDebugSession(session => {
      this.recordSessionEnd(session);
    });

    this.disposables.push(breakpointDisposable, sessionStartDisposable, sessionEndDisposable);
    return [breakpointDisposable, sessionStartDisposable, sessionEndDisposable];
  }

  /**
   * Record breakpoint changes.
   */
  private recordBreakpointChange(e: vscode.BreakpointsChangeEvent): void {
    const now = this.clock.nowMs();

    if (e.added.length > 0) {
      this.breakpointEvents.push({ tsMs: now, type: "added", count: e.added.length });
    }
    if (e.removed.length > 0) {
      this.breakpointEvents.push({ tsMs: now, type: "removed", count: e.removed.length });
    }
    if (e.changed.length > 0) {
      this.breakpointEvents.push({ tsMs: now, type: "changed", count: e.changed.length });
    }

    this.pruneEvents(now);
  }

  /**
   * Record the start of a debug session.
   */
  private recordSessionStart(session: vscode.DebugSession): void {
    const now = this.clock.nowMs();
    this.activeSessions.set(session.id, now);
  }

  /**
   * Record the end of a debug session.
   */
  private recordSessionEnd(session: vscode.DebugSession): void {
    const now = this.clock.nowMs();
    const startTsMs = this.activeSessions.get(session.id);

    if (startTsMs !== undefined) {
      const durationMs = now - startTsMs;
      this.sessionEvents.push({
        tsMs: now,
        sessionId: session.id,
        startTsMs,
        endTsMs: now,
        durationMs,
      });
      this.activeSessions.delete(session.id);
    }

    this.pruneEvents(now);
  }

  /**
   * Evaluate the current debug patterns.
   * Debug detector is global (not file-scoped).
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();

    // Prune to window
    const windowStart = now - this.config.windowMs;
    const windowBreakpoints = this.breakpointEvents.filter(e => e.tsMs >= windowStart);
    const windowSessions = this.sessionEvents.filter(e => e.tsMs >= windowStart);

    // Calculate breakpoint thrashing
    const totalBreakpointChanges = windowBreakpoints.reduce((sum, e) => sum + e.count, 0);
    const breakpointThrashing = totalBreakpointChanges >= this.config.minBreakpointChanges;

    // Calculate short sessions
    const shortSessions = windowSessions.filter(
      s => s.durationMs < this.config.shortSessionThresholdMs
    );
    const hasShortSessions = shortSessions.length >= this.config.minShortSessions;

    // No significant patterns
    if (!breakpointThrashing && !hasShortSessions) return [];

    // Calculate score
    let score = 0;
    let shortSession = false;

    if (breakpointThrashing) {
      const breakpointScore = Math.min(
        1,
        totalBreakpointChanges / (this.config.minBreakpointChanges * 2)
      );
      score = Math.max(score, breakpointScore);
    }

    if (hasShortSessions) {
      const sessionScore = Math.min(1, shortSessions.length / (this.config.minShortSessions * 2));
      score = Math.max(score, sessionScore);
      shortSession = true;
    }

    // Get most recent short session duration
    const lastShortSession = shortSessions.sort((a, b) => b.tsMs - a.tsMs)[0];

    return [
      {
        type: "debug",
        score,
        tsMs: now,
        fileKey: null, // Debug signals are global
        metadata: {
          breakpointChanges: totalBreakpointChanges,
          sessionDurationMs: lastShortSession?.durationMs,
          shortSession,
        },
      },
    ];
  }

  private pruneEvents(now: number): void {
    const windowStart = now - this.config.windowMs;

    // Prune breakpoint events
    let idx = 0;
    while (idx < this.breakpointEvents.length && this.breakpointEvents[idx].tsMs < windowStart) {
      idx++;
    }
    if (idx > 0) this.breakpointEvents.splice(0, idx);

    // Prune session events
    idx = 0;
    while (idx < this.sessionEvents.length && this.sessionEvents[idx].tsMs < windowStart) {
      idx++;
    }
    if (idx > 0) this.sessionEvents.splice(0, idx);

    // Limit total events
    if (this.breakpointEvents.length > this.config.maxEvents) {
      this.breakpointEvents.splice(0, this.breakpointEvents.length - this.config.maxEvents);
    }
    if (this.sessionEvents.length > this.config.maxEvents) {
      this.sessionEvents.splice(0, this.sessionEvents.length - this.config.maxEvents);
    }
  }

  reset(_fileKey: string | null): void {
    // Debug detector is global, so we always reset everything
    this.breakpointEvents.length = 0;
    this.sessionEvents.length = 0;
    this.activeSessions.clear();
  }

  dispose(): void {
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables.length = 0;
    this.breakpointEvents.length = 0;
    this.sessionEvents.length = 0;
    this.activeSessions.clear();
  }
}
