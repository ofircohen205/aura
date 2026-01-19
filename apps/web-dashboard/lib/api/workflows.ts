import { apiClient } from "./client";
import type { WorkflowResponse, StruggleInput, AuditInput } from "@/types/api";

export const workflowsApi = {
  triggerStruggle: async (data: StruggleInput): Promise<WorkflowResponse> => {
    const response = await apiClient.post<WorkflowResponse>("/workflows/struggle", data);
    return response.data;
  },

  triggerAudit: async (data: AuditInput): Promise<WorkflowResponse> => {
    const response = await apiClient.post<WorkflowResponse>("/workflows/audit", data);
    return response.data;
  },
};
