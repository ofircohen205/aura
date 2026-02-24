import * as vscode from "vscode";
import type { Clock, StruggleDecision, StruggleDetectorConfig } from "./struggle-detector";
import { StruggleDetector } from "./struggle-detector";

export type StruggleServiceConfig = {
  windowMs: number;
  retryAttemptThreshold: number;
  cooldownMs: number;
  maxSnippetChars: number;
};

export type StruggleContext = {
  fileKey: string;
  filePath: string | null;
  languageId: string | null;
  snippet: string | null;
  line: number | null;
  diagnosticsErrors: string[];
};

export type StruggleDetection = {
  decision: StruggleDecision;
  context: StruggleContext;
};

function isFileDocument(doc: vscode.TextDocument): boolean {
  return doc.uri.scheme === "file";
}

function safeFsPath(uri: vscode.Uri): string | null {
  try {
    return uri.scheme === "file" ? uri.fsPath : null;
  } catch {
    return null;
  }
}

function extractSnippet(doc: vscode.TextDocument, line: number, maxChars: number): string {
  const startLine = Math.max(0, line - 2);
  const endLine = Math.min(doc.lineCount - 1, line + 2);
  const start = new vscode.Position(startLine, 0);
  const end = new vscode.Position(endLine, doc.lineAt(endLine).text.length);
  const snippet = doc.getText(new vscode.Range(start, end));
  return snippet.slice(0, maxChars);
}

function defaultDetectorConfig(windowMs: number): Omit<StruggleDetectorConfig, "windowMs"> {
  return {
    retryAttemptThreshold: 3,
    errorCountThreshold: 2,
    editFrequencyThresholdPerMin: 10,
    cooldownMs: 2 * 60_000,
    maxSnippetChars: 300,
    maxEventsPerFile: 200,
    maxErrorsPerFile: 20,
    levenshteinSimilarityThreshold: 0.2,
    maxComparisonsPerEdit: 10,
    maxLineDistanceForRetry: 2,
  };
}

export class StruggleService {
  private readonly clock: Clock;
  private readonly detector: StruggleDetector;
  private readonly diagnosticsByFileKey: Map<string, string[]> = new Map();

  constructor(config: StruggleServiceConfig, clock?: Clock) {
    this.clock =
      clock ??
      ({
        nowMs: () => Date.now(),
      } satisfies Clock);

    this.detector = new StruggleDetector(
      {
        windowMs: config.windowMs,
        ...defaultDetectorConfig(config.windowMs),
        retryAttemptThreshold: config.retryAttemptThreshold,
        cooldownMs: config.cooldownMs,
        maxSnippetChars: config.maxSnippetChars,
      },
      this.clock
    );
  }

  public onDocumentChanged(event: vscode.TextDocumentChangeEvent): StruggleDetection | null {
    const doc = event.document;
    if (!isFileDocument(doc)) return null;
    if (event.contentChanges.length === 0) return null;

    const now = this.clock.nowMs();
    const fileKey = doc.uri.toString();
    const primaryLine = event.contentChanges[0]?.range?.start?.line ?? 0;
    const snippet = extractSnippet(doc, primaryLine, 300);

    this.detector.recordEdit({
      tsMs: now,
      fileKey,
      snippet,
      line: primaryLine,
    });

    const decision = this.detector.evaluate(fileKey, now);
    if (!decision.shouldTrigger) return null;

    const diagnosticsErrors = this.diagnosticsByFileKey.get(fileKey) ?? [];

    return {
      decision,
      context: {
        fileKey,
        filePath: safeFsPath(doc.uri),
        languageId: doc.languageId ?? null,
        snippet,
        line: primaryLine,
        diagnosticsErrors,
      },
    };
  }

  public onDiagnosticsChanged(e: vscode.DiagnosticChangeEvent): void {
    const now = this.clock.nowMs();
    for (const uri of e.uris) {
      if (uri.scheme !== "file") continue;
      const diags = vscode.languages.getDiagnostics(uri);
      const errors = diags
        .filter(d => d.severity === vscode.DiagnosticSeverity.Error)
        .map(d => d.message)
        .filter(m => m && m.trim().length > 0);

      const fileKey = uri.toString();
      this.diagnosticsByFileKey.set(fileKey, errors);
      this.detector.replaceErrors(fileKey, errors, now);
    }
  }
}
