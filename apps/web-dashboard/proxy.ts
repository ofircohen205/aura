import { NextRequest, NextResponse } from "next/server";
import { ROUTES, isProtectedRoute, isAuthRoute, isSafeCallbackUrl } from "./lib/routes";

/**
 * Proxy for route protection and authentication redirects.
 * Runs on Node.js runtime before requests are processed.
 *
 * Note: For production, consider moving authentication logic to
 * Server Layout Guards or Route Handlers for better security.
 */
export async function proxy(request: NextRequest): Promise<NextResponse> {
  // DISABLED: Since we're using localStorage for tokens (client-side only),
  // the server-side middleware cannot access them. All authentication checks
  // are handled client-side by the ProtectedRoute component.
  //
  // This proxy is kept for potential future use if we switch to cookie-based auth.

  return NextResponse.next();

  // Original implementation (disabled):
  // const { pathname } = request.nextUrl;
  // const accessToken = request.cookies.get("access_token")?.value;
  //
  // if (isProtectedRoute(pathname) && !accessToken) {
  //   const loginUrl = new URL(ROUTES.AUTH.LOGIN, request.url);
  //   loginUrl.searchParams.set("callbackUrl", pathname + request.nextUrl.search);
  //   return NextResponse.redirect(loginUrl);
  // }
  //
  // if (isAuthRoute(pathname) && accessToken) {
  //   const callbackUrl = request.nextUrl.searchParams.get("callbackUrl");
  //   const redirectUrl =
  //     callbackUrl && isSafeCallbackUrl(callbackUrl) ? callbackUrl : ROUTES.DASHBOARD.ROOT;
  //   return NextResponse.redirect(new URL(redirectUrl, request.url));
  // }
}

// Configure which routes the proxy should run on
// Using ROUTES constants would be ideal, but Next.js matcher requires string literals
export const config = {
  matcher: ["/dashboard/:path*", "/auth/:path*"],
};
