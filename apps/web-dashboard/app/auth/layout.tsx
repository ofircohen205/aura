"use client";

import { Suspense } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import Link from "next/link";
import { ROUTES } from "@/lib/routes";

function AuthLayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuth();

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

  if (isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
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
