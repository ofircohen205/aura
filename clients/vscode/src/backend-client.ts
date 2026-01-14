import axios from "axios";
import * as vscode from "vscode";

export class BackendClient {
  private baseUrl: string = "http://localhost:8000";

  constructor() {}

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return response.status === 200;
    } catch (error) {
      console.error("Backend health check failed:", error);
      return false;
    }
  }

  async sendStruggleEvent(event: any): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/api/event`, event);
    } catch (error) {
      console.error("Failed to send struggle event:", error);
    }
  }
}
