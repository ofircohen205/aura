/**
 * Semantic Detector
 *
 * Detects struggle signals based on code structure changes.
 * Uses VSCode's document symbol provider for lightweight AST analysis.
 *
 * This detector is disabled by default as it has higher overhead.
 */

import * as vscode from "vscode";
import type { Clock, SignalDetector, SignalEvent } from "./types";

type SymbolSnapshot = {
  tsMs: number;
  fileKey: string;
  symbols: SymbolInfo[];
};

type SymbolInfo = {
  name: string;
  kind: vscode.SymbolKind;
  range: { start: number; end: number };
};

type SymbolChange = {
  type: "structural" | "cosmetic";
  added: number;
  removed: number;
  modified: number;
};

export type SemanticDetectorConfig = {
  /** Time window for tracking semantic changes in ms */
  windowMs: number;
  /** Minimum structural changes to generate a signal */
  minStructuralChanges: number;
  /** Debounce time for symbol analysis in ms */
  debounceMs: number;
  /** Maximum snapshots to keep per file */
  maxSnapshotsPerFile: number;
};

const DEFAULT_CONFIG: SemanticDetectorConfig = {
  windowMs: 5 * 60_000, // 5 minutes
  minStructuralChanges: 3,
  debounceMs: 1000, // 1 second debounce
  maxSnapshotsPerFile: 20,
};

/** Symbol kinds that represent structural elements */
const STRUCTURAL_KINDS = new Set([
  vscode.SymbolKind.Class,
  vscode.SymbolKind.Interface,
  vscode.SymbolKind.Function,
  vscode.SymbolKind.Method,
  vscode.SymbolKind.Constructor,
  vscode.SymbolKind.Enum,
  vscode.SymbolKind.Struct,
  vscode.SymbolKind.Module,
  vscode.SymbolKind.Namespace,
]);

/**
 * Detects semantic patterns that may indicate struggle.
 *
 * Patterns detected:
 * - Structural changes: Adding/removing functions, classes, etc.
 * - Cosmetic changes: Renaming, reformatting without structure changes
 * - Churn: High rate of structural changes without progress
 *
 * NOTE: This detector is optional and disabled by default due to overhead.
 */
export class SemanticDetector implements SignalDetector {
  public readonly type = "semantic" as const;

  private readonly clock: Clock;
  private readonly config: SemanticDetectorConfig;
  private readonly snapshotsByFile: Map<string, SymbolSnapshot[]> = new Map();
  private readonly debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private readonly pendingAnalysis: Map<string, vscode.TextDocument> = new Map();

  constructor(config?: Partial<SemanticDetectorConfig>, clock?: Clock) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.clock = clock ?? { nowMs: () => Date.now() };
  }

  /**
   * Schedule symbol analysis for a document.
   * Debounced to avoid excessive symbol provider calls.
   */
  scheduleAnalysis(document: vscode.TextDocument): void {
    if (document.uri.scheme !== "file") return;

    const fileKey = document.uri.toString();

    // Clear existing timer
    const existingTimer = this.debounceTimers.get(fileKey);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Store document reference for analysis
    this.pendingAnalysis.set(fileKey, document);

    // Schedule new analysis
    const timer = setTimeout(() => {
      this.debounceTimers.delete(fileKey);
      const doc = this.pendingAnalysis.get(fileKey);
      this.pendingAnalysis.delete(fileKey);

      if (doc) {
        void this.analyzeDocument(doc);
      }
    }, this.config.debounceMs);

    this.debounceTimers.set(fileKey, timer);
  }

  /**
   * Analyze document symbols and record a snapshot.
   */
  private async analyzeDocument(document: vscode.TextDocument): Promise<void> {
    const now = this.clock.nowMs();
    const fileKey = document.uri.toString();

    try {
      const symbols = await vscode.commands.executeCommand<vscode.DocumentSymbol[]>(
        "vscode.executeDocumentSymbolProvider",
        document.uri
      );

      if (!symbols) return;

      // Flatten nested symbols
      const flatSymbols = this.flattenSymbols(symbols);

      // Convert to simplified format
      const symbolInfos: SymbolInfo[] = flatSymbols.map(s => ({
        name: s.name,
        kind: s.kind,
        range: {
          start: document.offsetAt(s.range.start),
          end: document.offsetAt(s.range.end),
        },
      }));

      // Record snapshot
      const snapshots = this.getOrCreateSnapshots(fileKey);
      snapshots.push({
        tsMs: now,
        fileKey,
        symbols: symbolInfos,
      });

      this.pruneSnapshots(fileKey, now);
    } catch {
      // Symbol provider may not be available for all languages
    }
  }

  /**
   * Flatten nested document symbols.
   */
  private flattenSymbols(symbols: vscode.DocumentSymbol[]): vscode.DocumentSymbol[] {
    const result: vscode.DocumentSymbol[] = [];

    const flatten = (syms: vscode.DocumentSymbol[]) => {
      for (const sym of syms) {
        result.push(sym);
        if (sym.children && sym.children.length > 0) {
          flatten(sym.children);
        }
      }
    };

    flatten(symbols);
    return result;
  }

  /**
   * Evaluate the current semantic patterns for a file.
   */
  evaluate(fileKey: string | null, tsMs?: number): SignalEvent[] {
    const now = tsMs ?? this.clock.nowMs();
    const signals: SignalEvent[] = [];

    if (fileKey) {
      const signal = this.evaluateFile(fileKey, now);
      if (signal) signals.push(signal);
    } else {
      for (const key of this.snapshotsByFile.keys()) {
        const signal = this.evaluateFile(key, now);
        if (signal) signals.push(signal);
      }
    }

    return signals;
  }

  private evaluateFile(fileKey: string, now: number): SignalEvent | null {
    const snapshots = this.snapshotsByFile.get(fileKey);
    if (!snapshots || snapshots.length < 2) return null;

    // Prune to window
    const windowStart = now - this.config.windowMs;
    const windowSnapshots = snapshots.filter(s => s.tsMs >= windowStart);
    if (windowSnapshots.length < 2) return null;

    // Analyze changes between consecutive snapshots
    let totalStructuralChanges = 0;
    let totalCosmeticChanges = 0;
    let totalAdded = 0;
    let totalRemoved = 0;
    let totalModified = 0;

    for (let i = 1; i < windowSnapshots.length; i++) {
      const prev = windowSnapshots[i - 1];
      const curr = windowSnapshots[i];
      const change = this.compareSnapshots(prev, curr);

      if (change.type === "structural") {
        totalStructuralChanges++;
      } else {
        totalCosmeticChanges++;
      }
      totalAdded += change.added;
      totalRemoved += change.removed;
      totalModified += change.modified;
    }

    // No significant structural changes
    if (totalStructuralChanges < this.config.minStructuralChanges) return null;

    // Calculate score based on structural churn
    const score = Math.min(
      1,
      totalStructuralChanges / (this.config.minStructuralChanges * 2)
    );

    // Determine change type (more structural = more struggle)
    const changeType: "structural" | "cosmetic" | "unknown" =
      totalStructuralChanges > totalCosmeticChanges ? "structural" : "cosmetic";

    return {
      type: "semantic",
      score,
      tsMs: now,
      fileKey,
      metadata: {
        changeType,
        symbolChanges: {
          added: totalAdded,
          removed: totalRemoved,
          modified: totalModified,
        },
      },
    };
  }

  /**
   * Compare two snapshots and determine the type of change.
   */
  private compareSnapshots(prev: SymbolSnapshot, curr: SymbolSnapshot): SymbolChange {
    const prevByName = new Map<string, SymbolInfo>();
    for (const sym of prev.symbols) {
      prevByName.set(`${sym.kind}:${sym.name}`, sym);
    }

    const currByName = new Map<string, SymbolInfo>();
    for (const sym of curr.symbols) {
      currByName.set(`${sym.kind}:${sym.name}`, sym);
    }

    let added = 0;
    let removed = 0;
    let modified = 0;
    let structuralChanges = 0;

    // Check for removed symbols
    for (const [key, sym] of prevByName) {
      if (!currByName.has(key)) {
        removed++;
        if (STRUCTURAL_KINDS.has(sym.kind)) {
          structuralChanges++;
        }
      }
    }

    // Check for added/modified symbols
    for (const [key, sym] of currByName) {
      const prevSym = prevByName.get(key);
      if (!prevSym) {
        added++;
        if (STRUCTURAL_KINDS.has(sym.kind)) {
          structuralChanges++;
        }
      } else if (prevSym.range.start !== sym.range.start || prevSym.range.end !== sym.range.end) {
        modified++;
      }
    }

    const type = structuralChanges > 0 ? "structural" : "cosmetic";

    return { type, added, removed, modified };
  }

  private getOrCreateSnapshots(fileKey: string): SymbolSnapshot[] {
    let snapshots = this.snapshotsByFile.get(fileKey);
    if (!snapshots) {
      snapshots = [];
      this.snapshotsByFile.set(fileKey, snapshots);
    }
    return snapshots;
  }

  private pruneSnapshots(fileKey: string, now: number): void {
    const snapshots = this.snapshotsByFile.get(fileKey);
    if (!snapshots) return;

    const windowStart = now - this.config.windowMs;

    // Remove snapshots outside window
    let idx = 0;
    while (idx < snapshots.length && snapshots[idx].tsMs < windowStart) idx++;
    if (idx > 0) snapshots.splice(0, idx);

    // Limit size
    if (snapshots.length > this.config.maxSnapshotsPerFile) {
      snapshots.splice(0, snapshots.length - this.config.maxSnapshotsPerFile);
    }
  }

  reset(fileKey: string | null): void {
    if (fileKey) {
      this.snapshotsByFile.delete(fileKey);
      const timer = this.debounceTimers.get(fileKey);
      if (timer) {
        clearTimeout(timer);
        this.debounceTimers.delete(fileKey);
      }
      this.pendingAnalysis.delete(fileKey);
    } else {
      this.snapshotsByFile.clear();
      for (const timer of this.debounceTimers.values()) {
        clearTimeout(timer);
      }
      this.debounceTimers.clear();
      this.pendingAnalysis.clear();
    }
  }

  dispose(): void {
    for (const timer of this.debounceTimers.values()) {
      clearTimeout(timer);
    }
    this.debounceTimers.clear();
    this.snapshotsByFile.clear();
    this.pendingAnalysis.clear();
  }
}
