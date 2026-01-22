const BASE_ROUTES = {
  AUTH: "/auth",
  DASHBOARD: "/dashboard",
} as const;

function composeRoute(base: string, ...segments: string[]): string {
  const path = [base, ...segments].join("/");
  return path.replace(/\/+/g, "/").replace(/\/$/, "") || "/";
}

export const ROUTES = {
  HOME: "/",

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
    RAG: composeRoute(BASE_ROUTES.DASHBOARD, "rag"),
    PROFILE: composeRoute(BASE_ROUTES.DASHBOARD, "profile"),
    SETTINGS: composeRoute(BASE_ROUTES.DASHBOARD, "settings"),
  },
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES] extends string
  ? (typeof ROUTES)[keyof typeof ROUTES]
  : (typeof ROUTES)[keyof typeof ROUTES] extends (id: string) => string
    ? ReturnType<(typeof ROUTES)[keyof typeof ROUTES]>
    : never;

export type NavigationItem = {
  name: string;
  href: string;
};

export const NAVIGATION_ITEMS: readonly NavigationItem[] = [
  { name: "Dashboard", href: ROUTES.DASHBOARD.ROOT },
  { name: "Workflows", href: ROUTES.DASHBOARD.WORKFLOWS },
  { name: "Audits", href: ROUTES.DASHBOARD.AUDITS },
  { name: "RAG Explorer", href: ROUTES.DASHBOARD.RAG },
  { name: "Profile", href: ROUTES.DASHBOARD.PROFILE },
  { name: "Settings", href: ROUTES.DASHBOARD.SETTINGS },
] as const;

export function isProtectedRoute(pathname: string): boolean {
  return pathname.startsWith(ROUTES.DASHBOARD.BASE);
}

export function isAuthRoute(pathname: string): boolean {
  return pathname.startsWith(ROUTES.AUTH.BASE);
}

export function isSafeCallbackUrl(url: string): boolean {
  if (!url.startsWith(ROUTES.DASHBOARD.BASE)) {
    return false;
  }

  try {
    const parsed = new URL(url, "http://localhost");
    if (parsed.host && parsed.host !== "localhost") {
      return false;
    }
  } catch {}

  return true;
}

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
