import * as vscode from 'vscode';
import { StruggleService } from './struggle-service';
import { BackendClient } from './backend-client';
import { LessonPanel } from './lesson-panel';

export function activate(context: vscode.ExtensionContext) {
    console.log('Aura Guardian is now active!');

    const backendClient = new BackendClient();
    const struggleService = new StruggleService(backendClient);
    const lessonPanel = new LessonPanel();

    // Register Webview
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(LessonPanel.viewType, lessonPanel)
    );

    // Register Document Change Listener
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            struggleService.onDocumentChanged(event);
        })
    );

    // Initial Health Check
    backendClient.healthCheck().then(healthy => {
        if (healthy) {
            console.log('Connected to Aura Backend');
        } else {
            console.log('Could not connect to Aura Backend');
        }
    });
}

export function deactivate() { }
