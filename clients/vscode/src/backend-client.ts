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
  private csrfToken: string | null = null;

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
      this.tryCaptureCsrfTokenFromResponse(response.headers);
      return response.status === 200;
    } catch (error) {
      console.error("Backend health check failed:", error);
      return false;
    }
  }

  private tryCaptureCsrfTokenFromResponse(headers: Record<string, unknown>): void {
    // Starlette sets `set-cookie` which axios exposes in Node as string[] (usually).
    const raw = (headers as any)["set-cookie"] as unknown;
    const setCookies: string[] = Array.isArray(raw) ? raw : typeof raw === "string" ? [raw] : [];

    for (const cookie of setCookies) {
      // Example: "csrf-token=abc123; Max-Age=86400; Path=/; SameSite=strict"
      const match = cookie.match(/(?:^|;\s*)csrf-token=([^;]+)/);
      if (match?.[1]) {
        this.csrfToken = match[1];
        return;
      }
    }
  }

  private async ensureCsrfToken(): Promise<string | null> {
    if (this.csrfToken) return this.csrfToken;

    try {
      const response = await axios.get(`${this.getBaseUrl()}/health`, { timeout: 10_000 });
      this.tryCaptureCsrfTokenFromResponse(response.headers);
      return this.csrfToken;
    } catch (error) {
      console.error("Failed to fetch CSRF token from /health:", error);
      return null;
    }
  }

  private async buildCsrfHeaders(): Promise<Record<string, string>> {
    const token = await this.ensureCsrfToken();
    if (!token) return {};

    // Double-submit cookie pattern: cookie and header must match.
    return {
      "X-CSRF-Token": token,
      Cookie: `csrf-token=${token}`,
    };
  }

  async triggerStruggleWorkflow(
    payload: StruggleWorkflowRequest
  ): Promise<WorkflowResponse | null> {
    const url = `${this.getBaseUrl()}/api/v1/workflows/struggle`;

    const attempts = 3;
    const baseDelayMs = 250;

    for (let attempt = 1; attempt <= attempts; attempt++) {
      try {
        const csrfHeaders = await this.buildCsrfHeaders();
        const response = await axios.post<WorkflowResponse>(url, payload, {
          timeout: 10_000,
          headers: csrfHeaders,
        });
        return response.data;
      } catch (error) {
        const isLast = attempt === attempts;
        console.error("Failed to trigger struggle workflow:", error);
        // If CSRF token was missing/expired, refresh it once and retry.
        if (attempt === 1) this.csrfToken = null;
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
