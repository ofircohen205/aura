import * as assert from "assert";
import * as vscode from "vscode";
import { StruggleService } from "../struggle-service";
import { BackendClient } from "../backend-client";

suite("StruggleService Test Suite", () => {
  vscode.window.showInformationMessage("Start all tests.");

  test("Detects struggle on rapid edits", () => {
    // Mock BackendClient
    const mockBackend = new BackendClient();
    let sentEvent: any = null;
    mockBackend.sendStruggleEvent = async (event: any) => {
      sentEvent = event;
    };

    const service = new StruggleService(mockBackend);

    // Simulate rapid edits
    // We need to access private method or trigger 10 times
    for (let i = 0; i < 15; i++) {
      // Mock event - type is not important for this simple heuristic
      service.onDocumentChanged({} as any);
    }

    // Ideally we would mock Date.now() or ensure loop runs fast enough.
    // In this sync loop, it should be very fast (< 2 sec).

    // We can't easily assertion on the private state or the side effect (showInformationMessage)
    // without better mocking, but we can check if sendStruggleEvent was called if we mocked it correctly.

    // Note: In a real test setup we would use Sinon or Jest spies.
    // For this basic setup, we rely on the manual mock above.

    assert.ok(sentEvent, "Should have sent a struggle event");
    assert.strictEqual(sentEvent.type, "struggle");
  });
});
