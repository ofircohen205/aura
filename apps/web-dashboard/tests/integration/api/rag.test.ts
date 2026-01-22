import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ragApi } from "@/lib/api/rag";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import type { RAGQueryRequest, RAGQueryResponse, RAGStatsResponse } from "@/lib/api/rag";

// Mock axios
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe("RAG API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("query", () => {
    it("calls query endpoint with correct data", async () => {
      const mockResponse: RAGQueryResponse = {
        context: "Test context from RAG",
        query: "How do I use a for loop in Python?",
        top_k: 5,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const request: RAGQueryRequest = {
        query: "How do I use a for loop in Python?",
        error_patterns: ["NameError"],
        top_k: 5,
      };

      const result = await ragApi.query(request);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.RAG.QUERY, request);
      expect(result).toEqual(mockResponse);
    });

    it("calls query endpoint without error patterns", async () => {
      const mockResponse: RAGQueryResponse = {
        context: "Test context",
        query: "Python list comprehension",
        top_k: 3,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const request: RAGQueryRequest = {
        query: "Python list comprehension",
        top_k: 3,
      };

      const result = await ragApi.query(request);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.RAG.QUERY, request);
      expect(result).toEqual(mockResponse);
    });

    it("calls query endpoint with default top_k", async () => {
      const mockResponse: RAGQueryResponse = {
        context: "Test context",
        query: "TypeScript async await",
        top_k: 5,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const request: RAGQueryRequest = {
        query: "TypeScript async await",
      };

      const result = await ragApi.query(request);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.RAG.QUERY, request);
      expect(result).toEqual(mockResponse);
    });

    it("calls query endpoint with multiple error patterns", async () => {
      const mockResponse: RAGQueryResponse = {
        context: "Test context",
        query: "TypeError in Python",
        top_k: 10,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const request: RAGQueryRequest = {
        query: "TypeError in Python",
        error_patterns: [
          "TypeError: unsupported operand type",
          "NoneType object is not callable",
        ],
        top_k: 10,
      };

      const result = await ragApi.query(request);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.RAG.QUERY, request);
      expect(result).toEqual(mockResponse);
    });

    it("handles query errors correctly", async () => {
      const error = new Error("Network error");
      vi.mocked(apiClient.post).mockRejectedValue(error);

      const request: RAGQueryRequest = {
        query: "Test query",
      };

      await expect(ragApi.query(request)).rejects.toThrow("Network error");
    });
  });

  describe("getStats", () => {
    it("calls get stats endpoint", async () => {
      const mockResponse: RAGStatsResponse = {
        total_documents: 10,
        total_chunks: 100,
        documents_by_language: {
          python: 50,
          typescript: 30,
          java: 20,
        },
        documents_by_difficulty: {
          beginner: 40,
          intermediate: 35,
          advanced: 25,
        },
        collection_name: "test_collection",
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await ragApi.getStats();

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.RAG.STATS);
      expect(result).toEqual(mockResponse);
    });

    it("handles empty stats response", async () => {
      const mockResponse: RAGStatsResponse = {
        total_documents: 0,
        total_chunks: 0,
        documents_by_language: {},
        documents_by_difficulty: {},
        collection_name: null,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await ragApi.getStats();

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.RAG.STATS);
      expect(result).toEqual(mockResponse);
      expect(result.total_documents).toBe(0);
      expect(result.total_chunks).toBe(0);
    });

    it("handles stats errors correctly", async () => {
      const error = new Error("Service unavailable");
      vi.mocked(apiClient.get).mockRejectedValue(error);

      await expect(ragApi.getStats()).rejects.toThrow("Service unavailable");
    });

    it("handles stats with partial language breakdown", async () => {
      const mockResponse: RAGStatsResponse = {
        total_documents: 5,
        total_chunks: 50,
        documents_by_language: {
          python: 30,
        },
        documents_by_difficulty: {
          beginner: 20,
          intermediate: 20,
          advanced: 10,
        },
        collection_name: "test_collection",
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await ragApi.getStats();

      expect(result.documents_by_language.python).toBe(30);
      expect(result.documents_by_difficulty.beginner).toBe(20);
    });
  });
});
