/**
 * Navigation utility for client-side routing.
 * Provides a way to navigate that works in both client and server contexts.
 */

import { ROUTES, isSafeCallbackUrl } from "@/lib/routes";

/**
 * Navigate to a route. Uses Next.js router in client context,
 * falls back to window.location in server context or when router is unavailable.
 */
export function navigateTo(path: string) {
  if (typeof window === "undefined") {
    return; // Server-side, no navigation needed
  }

  // Try to use Next.js router if available (client-side)
  // This is a workaround since we can't import useRouter in a utility
  // Components should use useRouter directly, but this is for cases like interceptors
  if (window.location.pathname !== path) {
    window.location.href = path;
  }
}

/**
 * Build a callback URL for authentication redirects.
 * Validates that the URL is safe (starts with /dashboard).
 */
export function buildCallbackUrl(pathname: string, searchParams?: string): string | null {
  const fullPath = searchParams ? `${pathname}?${searchParams}` : pathname;

  // Only allow callback URLs that start with /dashboard for security
  if (isSafeCallbackUrl(fullPath)) {
    return fullPath;
  }

  return null;
}

/**
 * Extract and validate callback URL from search params.
 */
export function getCallbackUrl(searchParams: URLSearchParams): string | null {
  const callbackUrl = searchParams.get("callbackUrl");
  if (!callbackUrl) {
    return null;
  }

  // Validate that callback URL is safe
  return buildCallbackUrl(callbackUrl);
}

/**
 * Get page title from pathname.
 */
export function getPageTitle(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) {
    return "Dashboard";
  }

  if (segments[0] === "dashboard") {
    if (segments.length === 1) {
      return "Dashboard";
    }

    // Capitalize and format the page name
    const pageName = segments[1];
    return pageName.charAt(0).toUpperCase() + pageName.slice(1);
  }

  return "Aura Dashboard";
}

/**
 * Generate breadcrumb items from pathname.
 */
export interface BreadcrumbItem {
  label: string;
  href: string;
}

export function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split("/").filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];

  // Always start with Dashboard
  breadcrumbs.push({ label: "Dashboard", href: ROUTES.DASHBOARD.ROOT });

  if (segments.length <= 1 || segments[0] !== "dashboard") {
    return breadcrumbs;
  }

  // Build breadcrumbs for each segment
  let currentPath = ROUTES.DASHBOARD.ROOT;
  for (let i = 1; i < segments.length; i++) {
    const segment = segments[i];
    currentPath += `/${segment}`;

    // Format label (capitalize, replace hyphens with spaces)
    const label = segment
      .split("-")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    breadcrumbs.push({ label, href: currentPath });
  }

  return breadcrumbs;
}

/**
 * Check if a route is active, handling nested routes.
 * Returns true if the current pathname starts with the route.
 */
export function isRouteActive(pathname: string, route: string): boolean {
  if (pathname === route) {
    return true;
  }

  // For nested routes, check if pathname starts with route + "/"
  if (pathname.startsWith(route + "/")) {
    return true;
  }

  return false;
}
