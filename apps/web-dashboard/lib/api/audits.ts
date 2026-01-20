import { apiClient } from "./client";
import { ENDPOINTS } from "./endpoints";
import type { AuditResponse, PaginatedResponse, PaginationParams } from "@/types/api";

export const auditsApi = {
  triggerAudit: async (repoPath: string): Promise<AuditResponse> => {
    const response = await apiClient.post<AuditResponse>(ENDPOINTS.AUDITS.TRIGGER, {
      repo_path: repoPath,
    });
    return response.data;
  },

  list: async (params?: PaginationParams): Promise<PaginatedResponse<AuditResponse>> => {
    const response = await apiClient.get<PaginatedResponse<AuditResponse>>(ENDPOINTS.AUDITS.LIST, {
      params,
    });
    return response.data;
  },

  getById: async (auditId: string): Promise<AuditResponse> => {
    const response = await apiClient.get<AuditResponse>(ENDPOINTS.AUDITS.BY_ID(auditId));
    return response.data;
  },
};
