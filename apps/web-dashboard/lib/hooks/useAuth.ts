"use client";

import { useEffect, useRef } from "react";
import { create } from "zustand";
import { authApi } from "@/lib/api/auth";
import { logger } from "@/lib/utils/logger";
import type { User, UserLogin, UserRegister } from "@/types/api";

// Token storage utilities
const TOKEN_KEYS = {
  ACCESS: "access_token",
  REFRESH: "refresh_token",
} as const;

function getToken(key: keyof typeof TOKEN_KEYS): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEYS[key]);
}

function setToken(key: keyof typeof TOKEN_KEYS, value: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEYS[key], value);
}

function removeTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEYS.ACCESS);
  localStorage.removeItem(TOKEN_KEYS.REFRESH);
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>(set => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (credentials: UserLogin) => {
    try {
      const tokens = await authApi.login(credentials);
      setToken("ACCESS", tokens.access_token);
      setToken("REFRESH", tokens.refresh_token);
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (data: UserRegister) => {
    try {
      const tokens = await authApi.register(data);
      setToken("ACCESS", tokens.access_token);
      setToken("REFRESH", tokens.refresh_token);
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      const refreshToken = getToken("REFRESH");
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch (error) {
      // Continue with logout even if API call fails
      logger.error("Logout API call failed", error);
    } finally {
      removeTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  fetchUser: async () => {
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      removeTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));

export function useAuth() {
  const store = useAuthStore();
  const { user, isLoading, fetchUser, setUser } = store;
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Only run once on mount to avoid infinite loops
    if (hasInitialized.current) return;

    const token = getToken("ACCESS");
    if (token && !user && !isLoading) {
      hasInitialized.current = true;
      fetchUser();
    } else if (!token && user) {
      hasInitialized.current = true;
      setUser(null);
    } else if (!token && !user && isLoading) {
      hasInitialized.current = true;
      useAuthStore.setState({ isLoading: false });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - only run on mount

  // Listen for storage changes (e.g., logout in another tab)
  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === TOKEN_KEYS.ACCESS || e.key === TOKEN_KEYS.REFRESH) {
        const token = getToken("ACCESS");
        if (!token && user) {
          setUser(null);
        } else if (token && !user && !isLoading) {
          fetchUser();
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [user, isLoading, fetchUser, setUser]);

  return store;
}
