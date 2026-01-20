"use client";

import { usePathname } from "next/navigation";
import { useMemo, useCallback } from "react";
import { getPageTitle } from "@/lib/utils/navigation";
import { Breadcrumbs } from "./Breadcrumbs";
import { UserMenu } from "./UserMenu";
import { MobileMenu } from "./MobileMenu";
import { useState } from "react";

export function DashboardHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const pageTitle = useMemo(() => getPageTitle(pathname), [pathname]);

  const openMobileMenu = useCallback(() => {
    setMobileMenuOpen(true);
  }, []);

  const closeMobileMenu = useCallback(() => {
    setMobileMenuOpen(false);
  }, []);

  return (
    <>
      <header className="flex h-16 items-center justify-between border-b bg-card px-4 lg:px-6">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Mobile Menu Toggle */}
          <button
            type="button"
            onClick={openMobileMenu}
            className="lg:hidden rounded-md p-2 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            aria-label="Open navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            <span className="text-xl" aria-hidden="true">
              ☰
            </span>
          </button>

          <div className="flex flex-col min-w-0 flex-1">
            <h1 className="text-lg font-semibold truncate">{pageTitle}</h1>
            <div className="hidden md:block">
              <Breadcrumbs />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <UserMenu />
        </div>
      </header>

      <MobileMenu isOpen={mobileMenuOpen} onClose={closeMobileMenu} />
    </>
  );
}
