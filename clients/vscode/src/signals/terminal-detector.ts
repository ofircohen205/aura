/**
 * Terminal Detector
 *
 * Detects struggle signals from terminal output and task execution.
 * Monitors test failures, stack traces, and error patterns.
 */

import * as vscode from "vscode";
import type { Clock, SignalDetector, SignalEvent } from "./types";

type TerminalErrorEvent = {
  tsMs: number;
  errors: string[];
  exitCode: number | undefined;
  taskName: string | undefined;
  source: "task" | "terminal_data";
};

export type TerminalDetectorConfig = {
  /** Time window for tracking terminal events in ms */
  windowMs: number;
  /** Minimum failed tasks/commands to generate a signal */
  minFailedTasks: number;
  /** Maximum error messages to track */
  maxErrorMessages: number;
  /** Patterns that indicate test failures */
  testFailurePatterns: RegExp[];
  /** Patterns that indicate stack traces */
  stackTracePatterns: RegExp[];
};

const DEFAULT_CONFIG: TerminalDetectorConfig = {
  windowMs: 10 * 60_000, // 10 minutes
  minFailedTasks: 2,
  maxErrorMessages: 50,
  testFailurePatterns: [
    /FAIL(?:ED)?[:\s]/i,
    /\d+\s+(?:failing|failed)/i,
    /AssertionError/i,
    /Test\s+failed/i,
    /npm\s+ERR!/i,
    /Error:\s+expect/i,
    /✗|✕|×/, // Common test failure symbols
  ],
  stackTracePatterns: [
    /^\s+at\s+.+\(.+:\d+:\d+\)/m, // JavaScript stack traces
    /Traceback \(most recent call last\)/i, // Python tracebacks
    /^\s+File ".+", line \d+/m, // Python file lines
    /Exception in thread/i, // Java exceptions
    /panic:/i, // Go panics
    /error\[E\d+\]:/i, // Rust errors
  ],
};

/**
 * Detects terminal-based patterns that may indicate struggle.
 *
 * Patterns detected:
 * - Repeated test failures
 * - Stack traces in output
 * - Task execution failures (non-zero exit codes)
 */
export class TerminalDetector implements SignalDetector {
  public readonly type = "terminal" as const;

  private readonly clock: Clock;
  private readonly config: TerminalDetectorConfig;
  private readonly errorEvents: TerminalErrorEvent[] = [];
  private readonly disposables: vscode.Disposable[] = [];

  constructor(config?: Partial<TerminalDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Subscribe to VSCode task events.
   * Call this during extension activation.
   */
  subscribeToTasks(): vscode.Disposable {
    const disposable = vscode.tasks.onDidEndTaskProcess(e => {
      this.recordTaskEnd(e);
    });
    this.disposables.push(disposable);
    return disposable;
  }

  /**
   * Record the end of a task process.
   */
  private recordTaskEnd(e: vscode.TaskProcessEndEvent): void {
    const now = this.clock.nowMs();
    const exitCode = e.exitCode;
    const taskName = e.execution.task.name;

    // Only track failures (non-zero exit codes)
    if (exitCode === undefined || exitCode === 0) return;

    this.errorEvents.push({
      tsMs: now,
      errors: [`Task "${taskName}" failed with exit code ${exitCode}`],
      exitCode,
      taskName,
      source: "task",
    });

    this.pruneEvents(now);
  }

  /**
   * Record terminal output that may contain errors.
   * This can be called from terminal data handlers if available.
   */
  recordTerminalOutput(output: string, tsMs?: number): void {
    const now = tsMs ?? this.clock.nowMs();
    const errors: string[] = [];

    // Check for test failure patterns
    for (const pattern of this.config.testFailurePatterns) {
      if (pattern.test(output)) {
        // Extract relevant lines around the match
        const lines = output.split("\n");
        for (let i = 0; i < lines.length; i++) {
          if (pattern.test(lines[i])) {
            // Capture context: 2 lines before and after
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            const context = lines.slice(start, end).join("\n").trim();
            if (context.length > 0 && context.length < 500) {
              errors.push(context);
            }
            break;
          }
        }
        break;
      }
    }

    // Check for stack traces
    for (const pattern of this.config.stackTracePatterns) {
      if (pattern.test(output)) {
        // Extract the stack trace (limited to avoid huge captures)
        const match = output.match(pattern);
        if (match) {
          const startIdx = output.indexOf(match[0]);
          const excerpt = output.slice(startIdx, startIdx + 500);
          if (!errors.some(e => e.includes(excerpt.slice(0, 50)))) {
            errors.push(excerpt.trim());
          }
        }
        break;
      }
    }

    if (errors.length > 0) {
      this.errorEvents.push({
        tsMs: now,
        errors: errors.slice(0, 5), // Limit errors per event
        exitCode: undefined,
        taskName: undefined,
        source: "terminal_data",
      });

      this.pruneEvents(now);
    }
  }

  /**
   * Evaluate the current terminal patterns.
   * Terminal detector is global (not file-scoped).
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();

    // Prune to window
    const windowStart = now - this.config.windowMs;
    const windowEvents = this.errorEvents.filter(e => e.tsMs >= windowStart);

    if (windowEvents.length === 0) return [];

    // Count failures and collect errors
    const failedTasks = windowEvents.filter(e => e.source === "task").length;
    const terminalErrors = windowEvents.filter(e => e.source === "terminal_data").length;
    const allErrors = windowEvents.flatMap(e => e.errors);

    // Calculate score
    let score = 0;

    // Failed tasks are a strong signal
    if (failedTasks >= this.config.minFailedTasks) {
      score = Math.max(score, Math.min(1, failedTasks / (this.config.minFailedTasks * 2)));
    }

    // Terminal errors (stack traces, test failures) also contribute
    if (terminalErrors >= 1) {
      const terminalScore = Math.min(1, terminalErrors / 3);
      score = Math.max(score, terminalScore);
    }

    if (score === 0) return [];

    // Find most recent exit code
    const lastTaskEvent = windowEvents
      .filter(e => e.exitCode !== undefined)
      .sort((a, b) => b.tsMs - a.tsMs)[0];

    return [
      {
        type: "terminal",
        score,
        tsMs: now,
        fileKey: null, // Terminal signals are global
        metadata: {
          terminalErrors: allErrors.slice(0, 10), // Limit for payload size
          exitCode: lastTaskEvent?.exitCode,
          taskName: lastTaskEvent?.taskName,
        },
      },
    ];
  }

  private pruneEvents(now: number): void {
    const windowStart = now - this.config.windowMs;

    // Remove events outside window
    let idx = 0;
    while (idx < this.errorEvents.length && this.errorEvents[idx].tsMs < windowStart) idx++;
    if (idx > 0) this.errorEvents.splice(0, idx);

    // Limit total events
    if (this.errorEvents.length > this.config.maxErrorMessages) {
      this.errorEvents.splice(0, this.errorEvents.length - this.config.maxErrorMessages);
    }
  }

  reset(_fileKey: string | null): void {
    // Terminal detector is global, so we always reset everything
    this.errorEvents.length = 0;
  }

  dispose(): void {
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables.length = 0;
    this.errorEvents.length = 0;
  }
}
