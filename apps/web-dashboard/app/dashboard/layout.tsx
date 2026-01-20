"use client";

import { Suspense } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
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
      <ProtectedRoute>
        <div className="flex min-h-screen">
          <DashboardSidebar />
          <div className="flex flex-1 flex-col min-w-0">
            <DashboardHeader />
            <main id="main-content" className="flex-1 p-4 lg:p-6" tabIndex={-1}>
              {children}
            </main>
          </div>
        </div>
      </ProtectedRoute>
    </Suspense>
  );
}
