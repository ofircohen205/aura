import { ROUTES, isSafeCallbackUrl } from "@/lib/routes";

export function navigateTo(path: string) {
  if (typeof window === "undefined") {
    return;
  }

  if (window.location.pathname !== path) {
    window.location.href = path;
  }
}

export function buildCallbackUrl(pathname: string, searchParams?: string): string | null {
  const fullPath = searchParams ? `${pathname}?${searchParams}` : pathname;

  if (isSafeCallbackUrl(fullPath)) {
    return fullPath;
  }

  return null;
}

export function getCallbackUrl(searchParams: URLSearchParams): string | null {
  const callbackUrl = searchParams.get("callbackUrl");
  if (!callbackUrl) {
    return null;
  }

  return buildCallbackUrl(callbackUrl);
}

export function getPageTitle(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) {
    return "Dashboard";
  }

  if (segments[0] === "dashboard") {
    if (segments.length === 1) {
      return "Dashboard";
    }

    const pageName = segments[1];
    return pageName.charAt(0).toUpperCase() + pageName.slice(1);
  }

  return "Aura Dashboard";
}

export interface BreadcrumbItem {
  label: string;
  href: string;
}

export function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split("/").filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];

  breadcrumbs.push({ label: "Dashboard", href: ROUTES.DASHBOARD.ROOT });

  if (segments.length <= 1 || segments[0] !== "dashboard") {
    return breadcrumbs;
  }

  let currentPath = ROUTES.DASHBOARD.ROOT;
  for (let i = 1; i < segments.length; i++) {
    const segment = segments[i];
    currentPath += `/${segment}`;

    const label = segment
      .split("-")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    breadcrumbs.push({ label, href: currentPath });
  }

  return breadcrumbs;
}

export function isRouteActive(pathname: string, route: string): boolean {
  if (pathname === route) {
    return true;
  }

  if (pathname.startsWith(route + "/")) {
    return true;
  }

  return false;
}
