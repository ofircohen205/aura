/**
 * Time Pattern Detector
 *
 * Detects struggle patterns based on timing of edits.
 * Identifies hesitation, burst-after-pause, and start-stop patterns.
 */

import type { Clock, SignalDetector, SignalEvent } from "./types";

type EditTimestamp = {
  tsMs: number;
  fileKey: string;
};

export type TimePatternDetectorConfig = {
  /** Time window for tracking edit timestamps in ms */
  windowMs: number;
  /** Minimum pause duration to consider as hesitation in ms */
  hesitationThresholdMs: number;
  /** Maximum time between edits to be considered a "burst" in ms */
  burstGapMs: number;
  /** Minimum edits in a burst to be significant */
  minBurstEdits: number;
  /** Number of start-stop cycles to trigger */
  startStopThreshold: number;
  /** Maximum events to track per file */
  maxEventsPerFile: number;
};

const DEFAULT_CONFIG: TimePatternDetectorConfig = {
  windowMs: 5 * 60_000, // 5 minutes
  hesitationThresholdMs: 30_000, // 30 seconds
  burstGapMs: 2_000, // 2 seconds between burst edits
  minBurstEdits: 5, // At least 5 rapid edits
  startStopThreshold: 3, // 3 start-stop cycles
  maxEventsPerFile: 200,
};

type DetectedPattern = {
  type: "hesitation" | "burst_after_pause" | "start_stop";
  score: number;
  hesitationMs?: number;
  burstEditCount?: number;
  startStopCount?: number;
};

/**
 * Detects time-based patterns that may indicate struggle.
 *
 * Patterns detected:
 * - Hesitation: Long pauses suggesting confusion or research
 * - Burst after pause: Research -> rapid attempt cycle
 * - Start-stop: Repeated brief coding attempts
 */
export class TimePatternDetector implements SignalDetector {
  public readonly type = "time_pattern" as const;

  private readonly clock: Clock;
  private readonly config: TimePatternDetectorConfig;
  private readonly timestampsByFile: Map<string, EditTimestamp[]> = new Map();

  constructor(config?: Partial<TimePatternDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Record an edit timestamp.
   * Call this from onDidChangeTextDocument handler.
   */
  recordEdit(fileKey: string, tsMs?: number): void {
    const now = tsMs ?? this.clock.nowMs();

    const timestamps = this.getOrCreateTimestamps(fileKey);
    timestamps.push({ tsMs: now, fileKey });

    this.pruneTimestamps(fileKey, now);
  }

  /**
   * Evaluate the current time patterns for a file.
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();
    const signals: SignalEvent[] = [];

    if (fileKey) {
      const signal = this.evaluateFile(fileKey, now);
      if (signal) signals.push(signal);
    } else {
      for (const key of this.timestampsByFile.keys()) {
        const signal = this.evaluateFile(key, now);
        if (signal) signals.push(signal);
      }
    }

    return signals;
  }

  private evaluateFile(fileKey: string, now: number): SignalEvent | null {
    const timestamps = this.timestampsByFile.get(fileKey);
    if (!timestamps || timestamps.length < 2) return null;

    // Prune to window
    const windowStart = now - this.config.windowMs;
    const windowTimestamps = timestamps.filter(t => t.tsMs >= windowStart);
    if (windowTimestamps.length < 2) return null;

    // Detect all patterns and pick the strongest
    const patterns: DetectedPattern[] = [];

    const hesitation = this.detectHesitation(windowTimestamps, now);
    if (hesitation) patterns.push(hesitation);

    const burstAfterPause = this.detectBurstAfterPause(windowTimestamps);
    if (burstAfterPause) patterns.push(burstAfterPause);

    const startStop = this.detectStartStop(windowTimestamps);
    if (startStop) patterns.push(startStop);

    if (patterns.length === 0) return null;

    // Pick the strongest pattern
    patterns.sort((a, b) => b.score - a.score);
    const strongest = patterns[0];

    return {
      type: "time_pattern",
      score: strongest.score,
      tsMs: now,
      fileKey,
      metadata: {
        patternType: strongest.type,
        hesitationMs: strongest.hesitationMs,
        burstEditCount: strongest.burstEditCount,
      },
    };
  }

  /**
   * Detect long pauses indicating hesitation/confusion.
   * Only triggers if there's activity after the pause.
   */
  private detectHesitation(timestamps: EditTimestamp[], now: number): DetectedPattern | null {
    if (timestamps.length < 2) return null;

    // Find the longest gap followed by activity
    let maxHesitation = 0;
    let hasActivityAfterHesitation = false;

    for (let i = 1; i < timestamps.length; i++) {
      const gap = timestamps[i].tsMs - timestamps[i - 1].tsMs;
      if (gap > maxHesitation && gap >= this.config.hesitationThresholdMs) {
        maxHesitation = gap;
        // Check if there's activity after this gap
        hasActivityAfterHesitation =
          i < timestamps.length - 1 || now - timestamps[i].tsMs < this.config.burstGapMs * 3;
      }
    }

    if (maxHesitation < this.config.hesitationThresholdMs || !hasActivityAfterHesitation) {
      return null;
    }

    // Score based on hesitation duration (caps at 2 minutes for max score)
    const score = Math.min(1, maxHesitation / (2 * 60_000));

    return {
      type: "hesitation",
      score,
      hesitationMs: maxHesitation,
    };
  }

  /**
   * Detect burst of edits after a long pause (research -> attempt cycle).
   */
  private detectBurstAfterPause(timestamps: EditTimestamp[]): DetectedPattern | null {
    if (timestamps.length < this.config.minBurstEdits + 1) return null;

    // Look for a long pause followed by rapid edits
    for (let i = 1; i < timestamps.length - this.config.minBurstEdits; i++) {
      const gapBefore = timestamps[i].tsMs - timestamps[i - 1].tsMs;

      if (gapBefore >= this.config.hesitationThresholdMs) {
        // Found a pause, now check for burst after
        let burstCount = 1;
        for (let j = i + 1; j < timestamps.length; j++) {
          const burstGap = timestamps[j].tsMs - timestamps[j - 1].tsMs;
          if (burstGap <= this.config.burstGapMs) {
            burstCount++;
          } else {
            break;
          }
        }

        if (burstCount >= this.config.minBurstEdits) {
          // Score based on burst size and pause duration
          const pauseScore = Math.min(1, gapBefore / (2 * 60_000));
          const burstScore = Math.min(1, burstCount / (this.config.minBurstEdits * 2));
          const score = (pauseScore + burstScore) / 2;

          return {
            type: "burst_after_pause",
            score,
            hesitationMs: gapBefore,
            burstEditCount: burstCount,
          };
        }
      }
    }

    return null;
  }

  /**
   * Detect start-stop patterns (repeated brief coding attempts).
   */
  private detectStartStop(timestamps: EditTimestamp[]): DetectedPattern | null {
    if (timestamps.length < 4) return null;

    // A "start-stop" is: activity -> pause -> activity -> pause
    // Where activity is a cluster of edits within burstGapMs
    // And pause is longer than hesitationThresholdMs

    let startStopCount = 0;
    let i = 0;

    while (i < timestamps.length - 1) {
      // Find activity cluster
      let clusterEnd = i;
      while (clusterEnd < timestamps.length - 1) {
        const gap = timestamps[clusterEnd + 1].tsMs - timestamps[clusterEnd].tsMs;
        if (gap <= this.config.burstGapMs) {
          clusterEnd++;
        } else {
          break;
        }
      }

      // Check if there's a pause after this cluster
      if (clusterEnd < timestamps.length - 1) {
        const pauseGap = timestamps[clusterEnd + 1].tsMs - timestamps[clusterEnd].tsMs;
        if (pauseGap >= this.config.hesitationThresholdMs / 2) {
          startStopCount++;
        }
      }

      i = clusterEnd + 1;
    }

    if (startStopCount < this.config.startStopThreshold) return null;

    const score = Math.min(1, startStopCount / (this.config.startStopThreshold * 2));

    return {
      type: "start_stop",
      score,
      startStopCount,
    };
  }

  private getOrCreateTimestamps(fileKey: string): EditTimestamp[] {
    let timestamps = this.timestampsByFile.get(fileKey);
    if (!timestamps) {
      timestamps = [];
      this.timestampsByFile.set(fileKey, timestamps);
    }
    return timestamps;
  }

  private pruneTimestamps(fileKey: string, now: number): void {
    const timestamps = this.timestampsByFile.get(fileKey);
    if (!timestamps) return;

    const windowStart = now - this.config.windowMs;

    // Remove timestamps outside window
    let idx = 0;
    while (idx < timestamps.length && timestamps[idx].tsMs < windowStart) idx++;
    if (idx > 0) timestamps.splice(0, idx);

    // Limit size
    if (timestamps.length > this.config.maxEventsPerFile) {
      timestamps.splice(0, timestamps.length - this.config.maxEventsPerFile);
    }
  }

  reset(fileKey: string | null): void {
    if (fileKey) {
      this.timestampsByFile.delete(fileKey);
    } else {
      this.timestampsByFile.clear();
    }
  }

  dispose(): void {
    this.timestampsByFile.clear();
  }
}
