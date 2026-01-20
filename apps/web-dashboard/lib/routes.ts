/**
 * Centralized route definitions for the application.
 * Use these constants instead of hardcoding route paths throughout the codebase.
 *
 * Design Principles:
 * - Compose routes from base paths to avoid duplication
 * - Use functions for dynamic routes with proper typing
 * - Export types for better IDE support and type safety
 */

// Base route paths - single source of truth for route prefixes
const BASE_ROUTES = {
  AUTH: "/auth",
  DASHBOARD: "/dashboard",
} as const;

// Helper function to compose routes
function composeRoute(base: string, ...segments: string[]): string {
  const path = [base, ...segments].join("/");
  // Normalize double slashes and trailing slashes
  return path.replace(/\/+/g, "/").replace(/\/$/, "") || "/";
}

// Static route definitions
export const ROUTES = {
  // Root
  HOME: "/",

  // Authentication routes
  AUTH: {
    BASE: BASE_ROUTES.AUTH,
    LOGIN: composeRoute(BASE_ROUTES.AUTH, "login"),
    REGISTER: composeRoute(BASE_ROUTES.AUTH, "register"),
  },

  // Dashboard routes
  DASHBOARD: {
    BASE: BASE_ROUTES.DASHBOARD,
    ROOT: BASE_ROUTES.DASHBOARD,
    WORKFLOWS: composeRoute(BASE_ROUTES.DASHBOARD, "workflows"),
    WORKFLOW_DETAIL: (id: string) => composeRoute(BASE_ROUTES.DASHBOARD, "workflows", id),
    AUDITS: composeRoute(BASE_ROUTES.DASHBOARD, "audits"),
    AUDIT_DETAIL: (id: string) => composeRoute(BASE_ROUTES.DASHBOARD, "audits", id),
    PROFILE: composeRoute(BASE_ROUTES.DASHBOARD, "profile"),
    SETTINGS: composeRoute(BASE_ROUTES.DASHBOARD, "settings"),
  },
} as const;

/**
 * Type exports for better IDE support and type safety
 */
export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES] extends string
  ? (typeof ROUTES)[keyof typeof ROUTES]
  : (typeof ROUTES)[keyof typeof ROUTES] extends (id: string) => string
    ? ReturnType<(typeof ROUTES)[keyof typeof ROUTES]>
    : never;

export type NavigationItem = {
  name: string;
  href: string;
};

/**
 * Navigation items for sidebar and mobile menu.
 * Centralized navigation configuration.
 */
export const NAVIGATION_ITEMS: readonly NavigationItem[] = [
  { name: "Dashboard", href: ROUTES.DASHBOARD.ROOT },
  { name: "Workflows", href: ROUTES.DASHBOARD.WORKFLOWS },
  { name: "Audits", href: ROUTES.DASHBOARD.AUDITS },
  { name: "Profile", href: ROUTES.DASHBOARD.PROFILE },
  { name: "Settings", href: ROUTES.DASHBOARD.SETTINGS },
] as const;

/**
 * Check if a pathname is a protected route (requires authentication).
 * Uses the base dashboard route to match all dashboard sub-routes.
 */
export function isProtectedRoute(pathname: string): boolean {
  return pathname.startsWith(ROUTES.DASHBOARD.BASE);
}

/**
 * Check if a pathname is an auth route (login/register).
 * Checks against the auth base path to match all auth sub-routes.
 */
export function isAuthRoute(pathname: string): boolean {
  return pathname.startsWith(ROUTES.AUTH.BASE);
}

/**
 * Check if a callback URL is safe (starts with /dashboard).
 * Prevents open redirect vulnerabilities by only allowing dashboard routes.
 */
export function isSafeCallbackUrl(url: string): boolean {
  // Validate that URL starts with dashboard base and doesn't contain dangerous patterns
  if (!url.startsWith(ROUTES.DASHBOARD.BASE)) {
    return false;
  }

  // Additional security: ensure it's a valid path (no protocol, no host)
  try {
    const parsed = new URL(url, "http://localhost");
    // If URL parsing succeeds and has a host, it's an external URL (unsafe)
    if (parsed.host && parsed.host !== "localhost") {
      return false;
    }
  } catch {
    // If URL parsing fails, it's likely a relative path (safe)
  }

  return true;
}

/**
 * Build a route with query parameters.
 * @param path - Base route path
 * @param params - Query parameters object
 * @returns Route path with query string
 */
export function buildRouteWithParams(
  path: string,
  params: Record<string, string | number | boolean | undefined>
): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `${path}?${queryString}` : path;
}
