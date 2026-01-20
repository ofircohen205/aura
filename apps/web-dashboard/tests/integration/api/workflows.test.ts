import { describe, it, expect, vi, beforeEach } from "vitest";
import { workflowsApi } from "@/lib/api/workflows";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import type { WorkflowResponse, StruggleInput, AuditInput, PaginatedResponse } from "@/types/api";

// Mock axios
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe("Workflows API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("triggerStruggle", () => {
    it("calls trigger struggle endpoint with correct data", async () => {
      const mockResponse: WorkflowResponse = {
        thread_id: "thread-123",
        status: "completed",
        state: {},
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const struggleData: StruggleInput = {
        edit_frequency: 5.5,
        error_logs: ["error1", "error2"],
        history: ["history1"],
      };

      const result = await workflowsApi.triggerStruggle(struggleData);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.WORKFLOWS.STRUGGLE, struggleData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe("triggerAudit", () => {
    it("calls trigger audit endpoint with correct data", async () => {
      const mockResponse: WorkflowResponse = {
        thread_id: "thread-456",
        status: "completed",
        state: {},
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const auditData: AuditInput = {
        diff_content: "diff content here",
        violations: [],
      };

      const result = await workflowsApi.triggerAudit(auditData);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.WORKFLOWS.AUDIT, auditData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe("list", () => {
    it("calls list workflows endpoint", async () => {
      const mockResponse: PaginatedResponse<WorkflowResponse> = {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
        pages: 0,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await workflowsApi.list();

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.WORKFLOWS.LIST, { params: undefined });
      expect(result).toEqual(mockResponse);
    });

    it("calls list workflows endpoint with pagination params", async () => {
      const mockResponse: PaginatedResponse<WorkflowResponse> = {
        items: [],
        total: 0,
        page: 2,
        page_size: 10,
        pages: 0,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await workflowsApi.list({ page: 2, page_size: 10 });

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.WORKFLOWS.LIST, {
        params: { page: 2, page_size: 10 },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getById", () => {
    it("calls get workflow by id endpoint", async () => {
      const mockResponse: WorkflowResponse = {
        thread_id: "thread-123",
        status: "completed",
        state: {},
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await workflowsApi.getById("thread-123");

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.WORKFLOWS.BY_ID("thread-123"));
      expect(result).toEqual(mockResponse);
    });
  });
});
