import * as assert from "assert";
import { StruggleDetector } from "../struggle-detector";

suite("StruggleDetector Test Suite", () => {
  const createDetector = (nowMsRef: { value: number }) => {
    return new StruggleDetector(
      {
        windowMs: 5 * 60_000,
        retryAttemptThreshold: 3,
        errorCountThreshold: 2,
        editFrequencyThresholdPerMin: 10,
        cooldownMs: 0,
        maxSnippetChars: 300,
        maxEventsPerFile: 200,
        maxErrorsPerFile: 20,
        levenshteinSimilarityThreshold: 0.2,
        maxComparisonsPerEdit: 10,
        maxLineDistanceForRetry: 2,
      },
      { nowMs: () => nowMsRef.value }
    );
  };

  test("Detects struggle on retry attempts within window", () => {
    const now = { value: 1_000_000 };
    const detector = createDetector(now);
    const fileKey = "file:///tmp/example.ts";

    detector.recordEdit({ fileKey, snippet: "const x = 1;\n", line: 10 });
    assert.strictEqual(detector.evaluate(fileKey).shouldTrigger, false);

    now.value += 1_000;
    detector.recordEdit({ fileKey, snippet: "const x = 1;\n", line: 10 });
    assert.strictEqual(detector.evaluate(fileKey).shouldTrigger, false);

    now.value += 1_000;
    detector.recordEdit({ fileKey, snippet: "const x = 1;\n", line: 10 });
    const decision = detector.evaluate(fileKey);

    assert.strictEqual(decision.shouldTrigger, true);
    assert.strictEqual(decision.reason, "retries");
    assert.ok(decision.metrics.retryAttemptCount >= 3);
  });

  test("Detects struggle on error threshold", () => {
    const now = { value: 2_000_000 };
    const detector = createDetector(now);
    const fileKey = "file:///tmp/example.ts";

    detector.replaceErrors(fileKey, ["TS1005: ';' expected", "TS2304: Cannot find name 'x'"]);
    const decision = detector.evaluate(fileKey);
    assert.strictEqual(decision.shouldTrigger, true);
    assert.strictEqual(decision.reason, "errors");
  });
});
