export type Clock = {
  nowMs(): number;
};

export type StruggleDetectorConfig = {
  windowMs: number;
  retryAttemptThreshold: number; // number of similar attempts (including current) required
  errorCountThreshold: number;
  editFrequencyThresholdPerMin: number;
  cooldownMs: number;
  maxSnippetChars: number;
  maxEventsPerFile: number;
  maxErrorsPerFile: number;
  levenshteinSimilarityThreshold: number; // normalized distance in [0,1]; lower means more similar
  maxComparisonsPerEdit: number;
  maxLineDistanceForRetry: number;
};

export type EditEvent = {
  tsMs: number;
  fileKey: string;
  snippet: string;
  line: number;
};

export type ErrorEvent = {
  tsMs: number;
  fileKey: string;
  message: string;
};

export type StruggleMetrics = {
  windowMs: number;
  editCount: number;
  editFrequencyPerMin: number;
  errorCount: number;
  retryAttemptCount: number;
  retryCount: number; // retryAttemptCount - 1
};

export type StruggleDecisionReason = "retries" | "errors" | "frequency";

export type StruggleDecision = {
  shouldTrigger: boolean;
  reason: StruggleDecisionReason | null;
  metrics: StruggleMetrics;
};

type FileState = {
  edits: EditEvent[];
  errors: ErrorEvent[];
  lastTriggerTsMs: number | null;
};

export function levenshteinDistance(a: string, b: string): number {
  if (a === b) return 0;
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  // O(min(a,b)) memory DP
  const aChars = a;
  const bChars = b;
  const n = aChars.length;
  const m = bChars.length;

  let prev = new Array<number>(m + 1);
  let curr = new Array<number>(m + 1);

  for (let j = 0; j <= m; j++) prev[j] = j;

  for (let i = 1; i <= n; i++) {
    curr[0] = i;
    const ai = aChars.charCodeAt(i - 1);
    for (let j = 1; j <= m; j++) {
      const cost = ai === bChars.charCodeAt(j - 1) ? 0 : 1;
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
  // Collapse whitespace to reduce noisy diffs
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
  // Items are appended in time order; remove from front.
  let idx = 0;
  while (idx < items.length && items[idx].tsMs < windowStartMs) idx++;
  return idx === 0 ? items : items.slice(idx);
}

export class StruggleDetector {
  private readonly clock: Clock;
  private readonly config: StruggleDetectorConfig;
  private readonly byFile: Map<string, FileState> = new Map();

  constructor(config: StruggleDetectorConfig, clock: Clock) {
    this.config = config;
    this.clock = clock;
  }

  public recordEdit(e: Omit<EditEvent, "tsMs"> & { tsMs?: number }): void {
    const tsMs = e.tsMs ?? this.clock.nowMs();
    const state = this.getOrCreateState(e.fileKey);

    state.edits.push({
      tsMs,
      fileKey: e.fileKey,
      snippet: e.snippet.slice(0, this.config.maxSnippetChars),
      line: e.line,
    });

    const windowStart = tsMs - this.config.windowMs;
    state.edits = pruneToWindow(state.edits, windowStart);
    if (state.edits.length > this.config.maxEventsPerFile) {
      state.edits = state.edits.slice(-this.config.maxEventsPerFile);
    }
  }

  public replaceErrors(fileKey: string, messages: string[], tsMs?: number): void {
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

  public evaluate(fileKey: string, tsMs?: number): StruggleDecision {
    const now = tsMs ?? this.clock.nowMs();
    const state = this.getOrCreateState(fileKey);

    const windowStart = now - this.config.windowMs;
    state.edits = pruneToWindow(state.edits, windowStart);
    state.errors = pruneToWindow(state.errors, windowStart);

    const editCount = state.edits.length;
    const windowMinutes = this.config.windowMs / 60_000;
    const editFrequencyPerMin = windowMinutes > 0 ? editCount / windowMinutes : 0;

    const errorCount = state.errors.length;
    const retryAttemptCount = this.computeRetryAttemptCount(state);
    const retryCount = Math.max(0, retryAttemptCount - 1);

    const metrics: StruggleMetrics = {
      windowMs: this.config.windowMs,
      editCount,
      editFrequencyPerMin,
      errorCount,
      retryAttemptCount,
      retryCount,
    };

    const inCooldown =
      state.lastTriggerTsMs !== null && now - state.lastTriggerTsMs < this.config.cooldownMs;

    if (inCooldown) {
      return { shouldTrigger: false, reason: null, metrics };
    }

    if (retryAttemptCount >= this.config.retryAttemptThreshold) {
      state.lastTriggerTsMs = now;
      return { shouldTrigger: true, reason: "retries", metrics };
    }

    if (errorCount >= this.config.errorCountThreshold) {
      state.lastTriggerTsMs = now;
      return { shouldTrigger: true, reason: "errors", metrics };
    }

    if (editFrequencyPerMin >= this.config.editFrequencyThresholdPerMin) {
      state.lastTriggerTsMs = now;
      return { shouldTrigger: true, reason: "frequency", metrics };
    }

    return { shouldTrigger: false, reason: null, metrics };
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

    // Attempt count includes the current edit + similar prior edits.
    return 1 + similarCount;
  }

  private getOrCreateState(fileKey: string): FileState {
    const existing = this.byFile.get(fileKey);
    if (existing) return existing;

    const created: FileState = { edits: [], errors: [], lastTriggerTsMs: null };
    this.byFile.set(fileKey, created);
    return created;
  }
}
