import { apiClient } from "./client";
import { ENDPOINTS } from "./endpoints";

export interface RAGQueryRequest {
  query: string;
  error_patterns?: string[];
  top_k?: number;
}

export interface RAGQueryResponse {
  context: string;
  query: string;
  top_k: number;
}

export interface RAGStatsResponse {
  total_documents: number;
  total_chunks: number;
  documents_by_language: Record<string, number>;
  documents_by_difficulty: Record<string, number>;
  collection_name: string | null;
}

export const ragApi = {
  /**
   * Query the RAG vector store for relevant context
   */
  async query(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    const response = await apiClient.post<RAGQueryResponse>(ENDPOINTS.RAG.QUERY, request);
    return response.data;
  },

  /**
   * Get statistics about the RAG vector store
   */
  async getStats(): Promise<RAGStatsResponse> {
    const response = await apiClient.get<RAGStatsResponse>(ENDPOINTS.RAG.STATS);
    return response.data;
  },
};
