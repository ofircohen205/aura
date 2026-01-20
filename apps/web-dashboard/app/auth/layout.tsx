"use client";

import { Suspense, useEffect } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import Link from "next/link";
import { ROUTES, isSafeCallbackUrl } from "@/lib/routes";

function AuthLayoutContent({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Redirect to callback URL or dashboard
      const callbackUrl = searchParams.get("callbackUrl");
      const redirectUrl =
        callbackUrl && isSafeCallbackUrl(callbackUrl) ? callbackUrl : ROUTES.DASHBOARD.ROOT;
      router.push(redirectUrl);
    }
  }, [isAuthenticated, isLoading, router, searchParams]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="text-center">
          <div
            className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"
            aria-hidden="true"
          ></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render auth pages if already authenticated (redirect will happen)
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link
            href="/"
            className="text-xl font-bold focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded"
          >
            Aura
          </Link>
          <nav>
            <Link
              href={pathname === ROUTES.AUTH.LOGIN ? ROUTES.AUTH.REGISTER : ROUTES.AUTH.LOGIN}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {pathname === ROUTES.AUTH.LOGIN ? "Create Account" : "Sign In"}
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center p-4">{children}</main>
    </div>
  );
}

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background p-4">
          <div className="text-center">
            <div
              className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"
              aria-hidden="true"
            ></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      }
    >
      <AuthLayoutContent>{children}</AuthLayoutContent>
    </Suspense>
  );
}
