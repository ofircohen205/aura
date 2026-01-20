/**
 * Centralized API endpoint definitions for the application.
 * Use these constants instead of hardcoding endpoint paths throughout the codebase.
 *
 * Design Principles:
 * - Compose endpoints from base paths to avoid duplication
 * - Use functions for dynamic endpoints with proper typing
 * - Export types for better IDE support and type safety
 */

// Base API paths - single source of truth for API prefixes
const BASE_API = "/api/v1" as const;

// Helper function to compose API endpoints
function composeEndpoint(base: string, ...segments: string[]): string {
  const path = [base, ...segments].join("/");
  // Normalize double slashes and trailing slashes
  return path.replace(/\/\/+/g, "/").replace(/\/$/, "") || base;
}

// Static endpoint definitions
export const ENDPOINTS = {
  // Authentication endpoints
  AUTH: {
    BASE: composeEndpoint(BASE_API, "auth"),
    REGISTER: composeEndpoint(BASE_API, "auth", "register"),
    LOGIN: composeEndpoint(BASE_API, "auth", "login"),
    REFRESH: composeEndpoint(BASE_API, "auth", "refresh"),
    LOGOUT: composeEndpoint(BASE_API, "auth", "logout"),
    ME: composeEndpoint(BASE_API, "auth", "me"),
  },

  // Workflow endpoints
  WORKFLOWS: {
    BASE: composeEndpoint(BASE_API, "workflows"),
    LIST: composeEndpoint(BASE_API, "workflows"),
    STRUGGLE: composeEndpoint(BASE_API, "workflows", "struggle"),
    AUDIT: composeEndpoint(BASE_API, "workflows", "audit"),
    BY_ID: (threadId: string) => composeEndpoint(BASE_API, "workflows", threadId),
  },

  // Audit endpoints
  AUDITS: {
    BASE: composeEndpoint(BASE_API, "audit"),
    LIST: composeEndpoint(BASE_API, "audit"),
    TRIGGER: composeEndpoint(BASE_API, "audit", "trigger"),
    BY_ID: (auditId: string) => composeEndpoint(BASE_API, "audit", auditId),
  },
} as const;

/**
 * Type exports for better IDE support and type safety
 */
export type EndpointPath = (typeof ENDPOINTS)[keyof typeof ENDPOINTS] extends string
  ? (typeof ENDPOINTS)[keyof typeof ENDPOINTS]
  : (typeof ENDPOINTS)[keyof typeof ENDPOINTS] extends (id: string) => string
    ? ReturnType<(typeof ENDPOINTS)[keyof typeof ENDPOINTS]>
    : never;
