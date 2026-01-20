"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { LoginForm } from "@/components/auth/LoginForm";
import { ROUTES, isSafeCallbackUrl } from "@/lib/routes";

function LoginPageContent() {
  const router = useRouter();
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

  // Don't render login form if already authenticated (redirect will happen)
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <LoginForm />
    </div>
  );
}

export default function LoginPage() {
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
      <LoginPageContent />
    </Suspense>
  );
}
