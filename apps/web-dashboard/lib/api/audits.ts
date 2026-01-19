import { apiClient } from "./client";
import type { AuditResponse } from "@/types/api";

export const auditsApi = {
  triggerAudit: async (repoPath: string): Promise<AuditResponse> => {
    const response = await apiClient.post<AuditResponse>("/audit/trigger", {
      repo_path: repoPath,
    });
    return response.data;
  },
};
