"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth, useAuthStore } from "@/lib/hooks/useAuth";
import { ROUTES } from "@/lib/routes";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace(ROUTES.DASHBOARD.ROOT);
      } else {
        const hasToken = typeof window !== "undefined" && localStorage.getItem("access_token");
        if (hasToken) {
          const timeoutId = setTimeout(() => {
            const authState = useAuthStore.getState();
            if (authState.isAuthenticated) {
              router.replace(ROUTES.DASHBOARD.ROOT);
            } else {
              router.replace(ROUTES.AUTH.LOGIN);
            }
          }, 100);
          return () => clearTimeout(timeoutId);
        } else {
          router.replace(ROUTES.AUTH.LOGIN);
        }
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <div className="text-center">
          <div
            className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"
            aria-hidden="true"
          ></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    </main>
  );
}
