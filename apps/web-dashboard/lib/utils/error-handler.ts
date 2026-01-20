/**
 * Error handling utilities for consistent error message extraction and display.
 */

import { AxiosError } from "axios";

export interface ApiError {
  message: string;
  statusCode?: number;
  details?: unknown;
}

/**
 * Extracts a user-friendly error message from various error types.
 */
export function extractErrorMessage(error: unknown): string {
  // Axios errors
  if (error instanceof AxiosError) {
    // Try to get error message from response
    if (error.response?.data) {
      const data = error.response.data;

      // Handle different response formats
      if (typeof data === "string") {
        return data;
      }

      if (typeof data === "object") {
        // Check common error message fields
        if ("message" in data && typeof data.message === "string") {
          return data.message;
        }
        if ("detail" in data && typeof data.detail === "string") {
          return data.detail;
        }
        if ("error" in data && typeof data.error === "string") {
          return data.error;
        }
      }
    }

    // Fallback to HTTP status message
    if (error.response?.status) {
      return getHttpErrorMessage(error.response.status);
    }

    // Network error
    if (error.code === "ECONNABORTED") {
      return "Request timeout. Please try again.";
    }

    if (error.code === "ERR_NETWORK") {
      return "Network error. Please check your connection.";
    }
  }

  // Standard Error objects
  if (error instanceof Error) {
    return error.message;
  }

  // String errors
  if (typeof error === "string") {
    return error;
  }

  // Unknown error type
  return "An unexpected error occurred. Please try again.";
}

/**
 * Gets a user-friendly message for HTTP status codes.
 */
function getHttpErrorMessage(statusCode: number): string {
  const messages: Record<number, string> = {
    400: "Invalid request. Please check your input.",
    401: "Authentication required. Please log in.",
    403: "You don't have permission to perform this action.",
    404: "The requested resource was not found.",
    409: "A conflict occurred. The resource may already exist.",
    422: "Validation error. Please check your input.",
    429: "Too many requests. Please try again later.",
    500: "Server error. Please try again later.",
    502: "Service temporarily unavailable. Please try again later.",
    503: "Service unavailable. Please try again later.",
  };

  return messages[statusCode] || `Error ${statusCode}. Please try again.`;
}

/**
 * Creates an ApiError object from an unknown error.
 */
export function createApiError(error: unknown): ApiError {
  const message = extractErrorMessage(error);

  if (error instanceof AxiosError) {
    return {
      message,
      statusCode: error.response?.status,
      details: error.response?.data,
    };
  }

  return {
    message,
  };
}
