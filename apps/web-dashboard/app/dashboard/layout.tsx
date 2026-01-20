"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
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
  );
}
