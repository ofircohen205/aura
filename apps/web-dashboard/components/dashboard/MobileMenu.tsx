"use client";

import { useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils/cn";
import { isRouteActive } from "@/lib/utils/navigation";
import { NAVIGATION_ITEMS, ROUTES } from "@/lib/routes";

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  const pathname = usePathname();
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const firstLinkRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    if (isOpen) {
      onClose();
    }
  }, [pathname]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    const menuElement = document.getElementById("mobile-menu");
    if (!menuElement) return;

    const focusableElements = Array.from(
      menuElement.querySelectorAll<HTMLElement>('a, button, [tabindex]:not([tabindex="-1"])')
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    firstElement?.focus();

    function handleTabKey(e: KeyboardEvent) {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    }

    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", handleTabKey);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("keydown", handleTabKey);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Menu Drawer */}
      <div
        id="mobile-menu"
        className={cn(
          "fixed left-0 top-0 bottom-0 w-64 bg-card border-r z-50 lg:hidden transform transition-transform duration-300 ease-in-out",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between border-b px-6">
            <h2 className="text-xl font-bold">
              <Link
                href={ROUTES.DASHBOARD.ROOT}
                onClick={onClose}
                className="focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded"
              >
                Aura
              </Link>
            </h2>
            <button
              onClick={onClose}
              className="rounded-md p-2 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              aria-label="Close menu"
            >
              <span className="text-2xl" aria-hidden="true">
                ×
              </span>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4" aria-label="Main navigation">
            {NAVIGATION_ITEMS.map(item => {
              const active = isRouteActive(pathname, item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
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
        </div>
      </div>
    </>
  );
}
