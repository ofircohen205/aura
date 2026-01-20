"use client";

import { useMemo, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { cn } from "@/lib/utils/cn";
import { isRouteActive } from "@/lib/utils/navigation";
import { getInitials } from "@/lib/utils/user";
import { NAVIGATION_ITEMS, ROUTES } from "@/lib/routes";

export function DashboardSidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  // Memoize user initials to avoid recalculation
  const userInitials = useMemo(() => {
    return user ? getInitials(user.username) : "";
  }, [user?.username]);

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r bg-card">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center border-b px-6">
          <h2 className="text-xl font-bold">
            <Link
              href={ROUTES.DASHBOARD.ROOT}
              className="focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded"
            >
              Aura
            </Link>
          </h2>
        </div>
        <nav className="flex-1 space-y-1 p-4" aria-label="Main navigation">
          {NAVIGATION_ITEMS.map(item => {
            const active = isRouteActive(pathname, item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
                aria-current={active ? "page" : undefined}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        {user && (
          <div className="border-t p-4">
            <Link
              href={ROUTES.DASHBOARD.PROFILE}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-medium">
                {userInitials}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.username}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
            </Link>
          </div>
        )}
      </div>
    </aside>
  );
}
