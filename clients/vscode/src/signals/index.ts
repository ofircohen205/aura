/**
 * Signal Detection System
 *
 * Exports all signal types, detectors, and the aggregator.
 */

// Types
export type {
  AggregatedStruggle,
  AggregatorConfig,
  Clock,
  SignalDetector,
  SignalEvent,
  SignalMetadata,
  SignalType,
  SignalWeights,
} from "./types";

export { DEFAULT_AGGREGATOR_CONFIG, DEFAULT_SIGNAL_WEIGHTS } from "./types";

// Aggregator
export { SignalAggregator } from "./signal-aggregator";

// Detectors
export { UndoRedoDetector } from "./undo-redo-detector";
export type { UndoRedoDetectorConfig } from "./undo-redo-detector";

export { TimePatternDetector } from "./time-pattern-detector";
export type { TimePatternDetectorConfig } from "./time-pattern-detector";

export { TerminalDetector } from "./terminal-detector";
export type { TerminalDetectorConfig } from "./terminal-detector";

export { DebugDetector } from "./debug-detector";
export type { DebugDetectorConfig } from "./debug-detector";

export { SemanticDetector } from "./semantic-detector";
export type { SemanticDetectorConfig } from "./semantic-detector";

export { EditPatternDetector, levenshteinDistance } from "./edit-pattern-detector";
export type { EditPatternDetectorConfig } from "./edit-pattern-detector";
