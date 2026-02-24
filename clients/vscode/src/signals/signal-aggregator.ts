/**
 * Signal Aggregator
 *
 * Combines multiple signal detectors with configurable weights to produce
 * aggregated struggle detection decisions.
 */

import type {
  AggregatedStruggle,
  AggregatorConfig,
  Clock,
  SignalDetector,
  SignalEvent,
  SignalType,
} from "./types";
import { DEFAULT_AGGREGATOR_CONFIG } from "./types";

type CooldownState = {
  lastTriggerTsMs: number | null;
};

/**
 * Aggregates signals from multiple detectors using weighted scoring.
 */
export class SignalAggregator {
  private readonly clock: Clock;
  private readonly config: AggregatorConfig;
  private readonly detectors: Map<SignalType, SignalDetector> = new Map();
  private readonly cooldownByFile: Map<string, CooldownState> = new Map();
  private globalCooldown: CooldownState = { lastTriggerTsMs: null };

  constructor(config?: Partial<AggregatorConfig>, clock?: Clock) {
    this.config = {
      ...DEFAULT_AGGREGATOR_CONFIG,
      ...config,
      weights: {
        ...DEFAULT_AGGREGATOR_CONFIG.weights,
        ...config?.weights,
      },
    };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Register a signal detector.
   */
  registerDetector(detector: SignalDetector): void {
    this.detectors.set(detector.type, detector);
  }

  /**
   * Unregister a signal detector.
   */
  unregisterDetector(type: SignalType): void {
    const detector = this.detectors.get(type);
    if (detector) {
      detector.dispose();
      this.detectors.delete(type);
    }
  }

  /**
   * Get a registered detector by type.
   */
  getDetector<T extends SignalDetector>(type: SignalType): T | undefined {
    return this.detectors.get(type) as T | undefined;
  }

  /**
   * Evaluate all registered detectors and aggregate their signals.
   *
   * @param fileKey Optional file key to scope the evaluation
   * @param tsMs Optional timestamp for evaluation
   * @returns Aggregated struggle decision
   */
  evaluate(fileKey: string | null, tsMs?: number): AggregatedStruggle {
    const now = tsMs ?? this.clock.nowMs();

    // Check cooldown
    if (this.isInCooldown(fileKey, now)) {
      return {
        shouldTrigger: false,
        combinedScore: 0,
        primarySignal: null,
        signals: [],
        tsMs: now,
        fileKey,
      };
    }

    // Collect signals from all detectors
    const signals: SignalEvent[] = [];
    for (const detector of this.detectors.values()) {
      const detectorSignals = detector.evaluate(fileKey, now);
      signals.push(...detectorSignals);
    }

    // Filter signals within the aggregation window
    const windowStart = now - this.config.windowMs;
    const windowSignals = signals.filter(s => s.tsMs >= windowStart);

    // Calculate weighted score
    const { combinedScore, primarySignal } = this.calculateScore(windowSignals);

    // Determine if we should trigger
    const shouldTrigger = combinedScore >= this.config.triggerThreshold;

    // Update cooldown if triggering
    if (shouldTrigger) {
      this.setCooldown(fileKey, now);
    }

    return {
      shouldTrigger,
      combinedScore,
      primarySignal,
      signals: windowSignals,
      tsMs: now,
      fileKey,
    };
  }

  /**
   * Calculate the combined weighted score from signals.
   */
  private calculateScore(signals: SignalEvent[]): {
    combinedScore: number;
    primarySignal: SignalType | null;
  } {
    if (signals.length === 0) {
      return { combinedScore: 0, primarySignal: null };
    }

    // Group signals by type and take the highest score for each type
    const scoreByType = new Map<SignalType, number>();
    for (const signal of signals) {
      const existing = scoreByType.get(signal.type) ?? 0;
      scoreByType.set(signal.type, Math.max(existing, signal.score));
    }

    // Calculate weighted sum
    let weightedSum = 0;
    let totalWeight = 0;
    let primarySignal: SignalType | null = null;
    let primaryContribution = 0;

    for (const [type, score] of scoreByType) {
      const weight = this.config.weights[type] ?? 0;
      const contribution = score * weight;
      weightedSum += contribution;
      totalWeight += weight;

      if (contribution > primaryContribution) {
        primaryContribution = contribution;
        primarySignal = type;
      }
    }

    // Normalize by total weight of active detectors
    const combinedScore = totalWeight > 0 ? weightedSum / totalWeight : 0;

    return { combinedScore: Math.min(1, combinedScore), primarySignal };
  }

  /**
   * Check if we're in cooldown for a given file.
   */
  private isInCooldown(fileKey: string | null, now: number): boolean {
    // Check file-specific cooldown first
    if (fileKey) {
      const fileCooldown = this.cooldownByFile.get(fileKey);
      if (
        fileCooldown?.lastTriggerTsMs &&
        now - fileCooldown.lastTriggerTsMs < this.config.cooldownMs
      ) {
        return true;
      }
    }

    // Check global cooldown
    if (
      this.globalCooldown.lastTriggerTsMs &&
      now - this.globalCooldown.lastTriggerTsMs < this.config.cooldownMs
    ) {
      return true;
    }

    return false;
  }

  /**
   * Set cooldown after a trigger.
   */
  private setCooldown(fileKey: string | null, now: number): void {
    if (fileKey) {
      this.cooldownByFile.set(fileKey, { lastTriggerTsMs: now });
    }
    this.globalCooldown.lastTriggerTsMs = now;
  }

  /**
   * Reset all detectors and cooldowns.
   */
  reset(fileKey: string | null = null): void {
    for (const detector of this.detectors.values()) {
      detector.reset(fileKey);
    }

    if (fileKey) {
      this.cooldownByFile.delete(fileKey);
    } else {
      this.cooldownByFile.clear();
      this.globalCooldown = { lastTriggerTsMs: null };
    }
  }

  /**
   * Dispose of all detectors and resources.
   */
  dispose(): void {
    for (const detector of this.detectors.values()) {
      detector.dispose();
    }
    this.detectors.clear();
    this.cooldownByFile.clear();
  }

  /**
   * Update configuration at runtime.
   */
  updateConfig(config: Partial<AggregatorConfig>): void {
    if (config.triggerThreshold !== undefined) {
      this.config.triggerThreshold = config.triggerThreshold;
    }
    if (config.cooldownMs !== undefined) {
      this.config.cooldownMs = config.cooldownMs;
    }
    if (config.windowMs !== undefined) {
      this.config.windowMs = config.windowMs;
    }
    if (config.weights) {
      Object.assign(this.config.weights, config.weights);
    }
  }

  /**
   * Get current configuration.
   */
  getConfig(): Readonly<AggregatorConfig> {
    return { ...this.config, weights: { ...this.config.weights } };
  }
}
