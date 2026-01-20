import { AxiosError } from "axios";

export interface ApiError {
  message: string;
  statusCode?: number;
  details?: unknown;
}

function extractMessageFromResponseData(data: unknown): string | null {
  if (typeof data === "string") {
    return data;
  }

  if (typeof data === "object" && data !== null) {
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

  return null;
}

export function extractErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response?.data) {
      const message = extractMessageFromResponseData(error.response.data);
      if (message) {
        return message;
      }
    }

    if (error.response?.status) {
      return getHttpErrorMessage(error.response.status);
    }

    if (error.code === "ECONNABORTED") {
      return "Request timeout. Please try again.";
    }

    if (error.code === "ERR_NETWORK") {
      return "Network error. Please check your connection.";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "An unexpected error occurred. Please try again.";
}

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
