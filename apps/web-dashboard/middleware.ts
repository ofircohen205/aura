import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ROUTES, isProtectedRoute, isAuthRoute, isSafeCallbackUrl } from "./lib/routes";

/**
 * Middleware for route protection and authentication redirects.
 * Runs on Edge Runtime before requests are processed.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for access token in cookies (set by backend or client)
  // Note: Since we're using localStorage for tokens, we'll rely on client-side
  // ProtectedRoute component for actual auth checks. This middleware handles
  // initial redirects and prevents obvious unauthorized access.
  const accessToken = request.cookies.get("access_token")?.value;

  // Redirect unauthenticated users from protected routes to login
  if (isProtectedRoute(pathname) && !accessToken) {
    const loginUrl = new URL(ROUTES.AUTH.LOGIN, request.url);
    // Preserve the intended destination as callback URL
    loginUrl.searchParams.set("callbackUrl", pathname + request.nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from auth pages to dashboard
  if (isAuthRoute(pathname) && accessToken) {
    // Check if there's a callback URL to redirect to
    const callbackUrl = request.nextUrl.searchParams.get("callbackUrl");
    const redirectUrl =
      callbackUrl && isSafeCallbackUrl(callbackUrl) ? callbackUrl : ROUTES.DASHBOARD.ROOT;
    return NextResponse.redirect(new URL(redirectUrl, request.url));
  }

  return NextResponse.next();
}

// Configure which routes the middleware should run on
// Using ROUTES constants would be ideal, but Next.js matcher requires string literals
export const config = {
  matcher: ["/dashboard/:path*", "/auth/:path*"],
};
