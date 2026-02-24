/**
 * Core types for the multi-signal struggle detection system.
 */

/**
 * Signal types representing different sources of struggle detection.
 */
export type SignalType =
  | "undo_redo"
  | "time_pattern"
  | "terminal"
  | "debug"
  | "semantic"
  | "edit_pattern";

/**
 * A single signal event emitted by a detector.
 */
export type SignalEvent = {
  /** Type of signal that was detected */
  type: SignalType;
  /** Confidence score for this signal (0-1) */
  score: number;
  /** Timestamp when the signal was detected */
  tsMs: number;
  /** File key (URI string) where the signal was detected, if applicable */
  fileKey: string | null;
  /** Additional metadata specific to this signal type */
  metadata: SignalMetadata;
};

/**
 * Metadata specific to each signal type.
 */
export type SignalMetadata = {
  /** For undo_redo: pattern description like "undo-redo-undo cycle" */
  pattern?: string;
  /** For undo_redo: number of undo operations in window */
  undoCount?: number;
  /** For undo_redo: number of redo operations in window */
  redoCount?: number;

  /** For time_pattern: longest pause before rapid edits in ms */
  hesitationMs?: number;
  /** For time_pattern: detected pattern type */
  patternType?: "hesitation" | "burst_after_pause" | "start_stop";
  /** For time_pattern: number of edits in burst */
  burstEditCount?: number;

  /** For terminal: stack traces or error messages */
  terminalErrors?: string[];
  /** For terminal: exit code if available */
  exitCode?: number;
  /** For terminal: task name if from a task */
  taskName?: string;

  /** For debug: number of breakpoint changes */
  breakpointChanges?: number;
  /** For debug: debug session duration in ms */
  sessionDurationMs?: number;
  /** For debug: whether session was "short" (< threshold) */
  shortSession?: boolean;

  /** For semantic: change classification */
  changeType?: "structural" | "cosmetic" | "unknown";
  /** For semantic: symbols added/removed/modified counts */
  symbolChanges?: { added: number; removed: number; modified: number };

  /** For edit_pattern: Levenshtein-based retry count (legacy) */
  retryCount?: number;
  /** For edit_pattern: edit frequency per minute */
  editFrequencyPerMin?: number;
  /** For edit_pattern: error count in window */
  errorCount?: number;
};

/**
 * Configuration for signal weights in aggregation.
 */
export type SignalWeights = {
  undo_redo: number;
  time_pattern: number;
  terminal: number;
  debug: number;
  semantic: number;
  edit_pattern: number;
};

/**
 * Default weights for signal aggregation.
 */
export const DEFAULT_SIGNAL_WEIGHTS: SignalWeights = {
  undo_redo: 0.25,
  time_pattern: 0.2,
  terminal: 0.2,
  debug: 0.15,
  semantic: 0.1,
  edit_pattern: 0.1,
};

/**
 * Result of aggregating multiple signals.
 */
export type AggregatedStruggle = {
  /** Whether the combined score exceeds the trigger threshold */
  shouldTrigger: boolean;
  /** Combined weighted score (0-1) */
  combinedScore: number;
  /** The primary signal that contributed most to the score */
  primarySignal: SignalType | null;
  /** All contributing signals with their details */
  signals: SignalEvent[];
  /** Timestamp of evaluation */
  tsMs: number;
  /** File key if the struggle is file-specific */
  fileKey: string | null;
};

/**
 * Clock interface for testability.
 */
export type Clock = {
  nowMs(): number;
};

/**
 * Interface that all signal detectors must implement.
 */
export interface SignalDetector {
  /** The type of signal this detector produces */
  readonly type: SignalType;

  /**
   * Evaluate the current state and return any detected signals.
   * @param fileKey Optional file key to scope the evaluation
   * @param tsMs Optional timestamp for evaluation (defaults to now)
   * @returns Array of detected signal events (may be empty)
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[];

  /**
   * Reset the detector state, optionally scoped to a specific file.
   * @param fileKey Optional file key to reset (if null, resets all)
   */
  reset(fileKey: string | null): void;

  /**
   * Dispose of any resources held by the detector.
   */
  dispose(): void;
}

/**
 * Configuration for the signal aggregator.
 */
export type AggregatorConfig = {
  /** Threshold for combined score to trigger (0-1) */
  triggerThreshold: number;
  /** Weights for each signal type */
  weights: SignalWeights;
  /** Cooldown period after a trigger in ms */
  cooldownMs: number;
  /** Time window for signal aggregation in ms */
  windowMs: number;
};

/**
 * Default aggregator configuration.
 */
export const DEFAULT_AGGREGATOR_CONFIG: AggregatorConfig = {
  triggerThreshold: 0.6,
  weights: DEFAULT_SIGNAL_WEIGHTS,
  cooldownMs: 2 * 60_000, // 2 minutes
  windowMs: 5 * 60_000, // 5 minutes
};
