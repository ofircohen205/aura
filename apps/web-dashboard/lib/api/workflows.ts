import { apiClient } from "./client";
import { ENDPOINTS } from "./endpoints";
import type {
  WorkflowResponse,
  StruggleInput,
  AuditInput,
  PaginatedResponse,
  PaginationParams,
} from "@/types/api";

export const workflowsApi = {
  triggerStruggle: async (data: StruggleInput): Promise<WorkflowResponse> => {
    const response = await apiClient.post<WorkflowResponse>(ENDPOINTS.WORKFLOWS.STRUGGLE, data);
    return response.data;
  },

  triggerAudit: async (data: AuditInput): Promise<WorkflowResponse> => {
    const response = await apiClient.post<WorkflowResponse>(ENDPOINTS.WORKFLOWS.AUDIT, data);
    return response.data;
  },

  list: async (params?: PaginationParams): Promise<PaginatedResponse<WorkflowResponse>> => {
    const response = await apiClient.get<PaginatedResponse<WorkflowResponse>>(
      ENDPOINTS.WORKFLOWS.LIST,
      {
        params,
      }
    );
    return response.data;
  },

  getById: async (threadId: string): Promise<WorkflowResponse> => {
    const response = await apiClient.get<WorkflowResponse>(ENDPOINTS.WORKFLOWS.BY_ID(threadId));
    return response.data;
  },
};
