import axios from "axios";
import * as vscode from "vscode";

export type StruggleWorkflowRequest = {
  edit_frequency: number;
  error_logs: string[];
  history: string[];
  // Optional context fields (backend may ignore if not supported)
  source?: string;
  file_path?: string | null;
  language_id?: string | null;
  code_snippet?: string | null;
  client_timestamp?: number;
  struggle_reason?: string | null;
  retry_count?: number;
};

export type WorkflowResponse = {
  thread_id: string;
  status: string;
  state?: Record<string, unknown> | null;
  created_at: string;
  type: string;
};

export class BackendClient {
  private readonly defaultBaseUrl: string = "http://localhost:8000";

  constructor() {}

  private normalizeBaseUrl(input: string): string {
    const trimmed = input.trim();
    if (!trimmed) return this.defaultBaseUrl;

    try {
      const url = new URL(trimmed);
      if (url.protocol !== "http:" && url.protocol !== "https:") {
        throw new Error("Unsupported protocol");
      }
      // Use origin to avoid surprising path concatenation.
      return url.origin;
    } catch {
      console.warn("Invalid aura.baseUrl, falling back to default:", input);
      return this.defaultBaseUrl;
    }
  }

  private getBaseUrl(): string {
    const cfg = vscode.workspace.getConfiguration("aura");
    const raw = cfg.get<string>("baseUrl", this.defaultBaseUrl);
    return this.normalizeBaseUrl(raw);
  }

  private async sleep(ms: number): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, ms));
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.getBaseUrl()}/health`);
      return response.status === 200;
    } catch (error) {
      console.error("Backend health check failed:", error);
      return false;
    }
  }

  async triggerStruggleWorkflow(
    payload: StruggleWorkflowRequest
  ): Promise<WorkflowResponse | null> {
    const url = `${this.getBaseUrl()}/api/v1/workflows/struggle`;

    const attempts = 3;
    const baseDelayMs = 250;

    for (let attempt = 1; attempt <= attempts; attempt++) {
      try {
        const response = await axios.post<WorkflowResponse>(url, payload, {
          timeout: 10_000,
        });
        return response.data;
      } catch (error) {
        const isLast = attempt === attempts;
        console.error("Failed to trigger struggle workflow:", error);
        if (isLast) return null;

        const backoffMs = baseDelayMs * Math.pow(2, attempt - 1);
        await this.sleep(backoffMs);
      }
    }

    return null;
  }

  /**
   * Backward-compatible alias.
   * Prefer `triggerStruggleWorkflow`.
   */
  async sendStruggleEvent(event: any): Promise<void> {
    await this.triggerStruggleWorkflow(event as StruggleWorkflowRequest);
  }
}
