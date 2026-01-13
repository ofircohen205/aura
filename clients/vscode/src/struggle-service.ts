import * as vscode from 'vscode';
import { BackendClient } from './backend-client';

export class StruggleService {
    private backendClient: BackendClient;
    private editCount: number = 0;
    private lastEditTime: number = Date.now();
    private readonly THRESHOLD_time = 2000; // 2 seconds
    private readonly THRESHOLD_edits = 10; // 10 edits in 2 seconds

    constructor(backendClient: BackendClient) {
        this.backendClient = backendClient;
    }

    public onDocumentChanged(event: vscode.TextDocumentChangeEvent) {
        // Simple heuristic: rapid edits
        const now = Date.now();
        if (now - this.lastEditTime < this.THRESHOLD_time) {
            this.editCount++;
        } else {
            this.editCount = 1;
        }
        this.lastEditTime = now;

        if (this.editCount >= this.THRESHOLD_edits) {
            this.triggerStruggleDetected();
            this.editCount = 0; // Reset
        }
    }

    private triggerStruggleDetected() {
        vscode.window.showInformationMessage('Aura: Struggle Detected! (Simulation)');
        console.log('Struggle Detected');
        // In real impl, we would send context to backend
        this.backendClient.sendStruggleEvent({
            type: 'struggle',
            timestamp: Date.now()
        });
    }
}
