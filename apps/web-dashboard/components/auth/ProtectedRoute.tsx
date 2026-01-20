"use client";

import { useEffect } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { useAuth, useAuthStore } from "@/lib/hooks/useAuth";
import { ROUTES } from "@/lib/routes";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

function buildLoginUrl(pathname: string, searchParams: URLSearchParams): string {
  const fullPath = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : "");
  return `${ROUTES.AUTH.LOGIN}?callbackUrl=${encodeURIComponent(fullPath)}`;
}

function shouldWaitForAuthSync(): boolean {
  return typeof window !== "undefined" && localStorage.getItem("access_token") !== null;
}

function redirectToLogin(
  router: ReturnType<typeof useRouter>,
  pathname: string,
  searchParams: URLSearchParams
) {
  const loginUrl = buildLoginUrl(pathname, searchParams);
  router.replace(loginUrl);
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading, user } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    const isUnauthenticated = !isAuthenticated && !user;
    if (!isUnauthenticated) return;

    const shouldWait = shouldWaitForAuthSync();
    if (shouldWait) {
      const timeoutId = setTimeout(() => {
        const currentState = useAuthStore.getState();
        const stillUnauthenticated =
          !currentState.isAuthenticated && !currentState.isLoading && !currentState.user;
        if (stillUnauthenticated) {
          redirectToLogin(router, pathname, searchParams);
        }
      }, 500);

      return () => clearTimeout(timeoutId);
    }

    redirectToLogin(router, pathname, searchParams);
  }, [isAuthenticated, isLoading, user, router, pathname, searchParams]);

  if (isLoading) {
    return (
      <div
        className="flex min-h-screen items-center justify-center"
        role="status"
        aria-live="polite"
      >
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

  if (!isAuthenticated) {
    // Show loading state while redirect is happening instead of blank screen
    return (
      <div
        className="flex min-h-screen items-center justify-center"
        role="status"
        aria-live="polite"
      >
        <div className="text-center">
          <div
            className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"
            aria-hidden="true"
          ></div>
          <p className="text-muted-foreground">Redirecting...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
