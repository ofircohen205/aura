"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/hooks/useAuth";
import { ROUTES } from "@/lib/routes";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";
import { getInitials } from "@/lib/utils/user";

export function UserMenu() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Memoize close handler
  const closeMenu = useCallback(() => {
    setIsOpen(false);
    // Return focus to trigger button for accessibility
    setTimeout(() => {
      triggerRef.current?.focus();
    }, 0);
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        closeMenu();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, closeMenu]);

  // Close menu on Escape key
  useEffect(() => {
    if (!isOpen) return;

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        closeMenu();
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, closeMenu]);

  const handleLogout = useCallback(async () => {
    closeMenu();
    await logout();
    router.push(ROUTES.AUTH.LOGIN);
  }, [closeMenu, logout, router]);

  // Memoize user initials
  const userInitials = useMemo(() => {
    return user ? getInitials(user.username) : "";
  }, [user?.username]);

  if (!user) {
    return null;
  }

  const toggleMenu = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button
        ref={triggerRef}
        type="button"
        onClick={toggleMenu}
        className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 transition-colors"
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="User menu"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-medium">
          {userInitials}
        </div>
        <span className="hidden md:inline-block text-muted-foreground">{user.username}</span>
      </button>

      {isOpen && (
        <>
          {/* Overlay */}
          <div className="fixed inset-0 z-40" onClick={closeMenu} aria-hidden="true" />

          {/* Dropdown Menu */}
          <div
            className="absolute right-0 mt-2 w-56 rounded-md border bg-card shadow-lg z-50"
            role="menu"
            aria-orientation="vertical"
          >
            <div className="p-2">
              <div className="px-3 py-2 border-b">
                <p className="text-sm font-medium">{user.username}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>

              <div className="py-1">
                <Link
                  href={ROUTES.DASHBOARD.PROFILE}
                  onClick={closeMenu}
                  className="block px-3 py-2 text-sm text-foreground hover:bg-accent rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  role="menuitem"
                >
                  Profile
                </Link>
                <Link
                  href={ROUTES.DASHBOARD.SETTINGS}
                  onClick={closeMenu}
                  className="block px-3 py-2 text-sm text-foreground hover:bg-accent rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  role="menuitem"
                >
                  Settings
                </Link>
              </div>

              <div className="border-t pt-1">
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  role="menuitem"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
