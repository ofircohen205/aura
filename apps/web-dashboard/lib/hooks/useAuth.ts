"use client";

import { useEffect, useRef } from "react";
import { create } from "zustand";
import { authApi } from "@/lib/api/auth";
import { logger } from "@/lib/utils/logger";
import type { User, UserLogin, UserRegister } from "@/types/api";

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
      logger.error("Logout API call failed", error);
    } finally {
      removeTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  fetchUser: async () => {
    set({ isLoading: true });
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
      logger.info("User fetched successfully", { userId: user.id });
    } catch (error: any) {
      logger.error("Failed to fetch user", error, {
        status: error?.response?.status,
        message: error?.message,
      });
      const isUnauthorized = error?.response?.status === 401;
      if (isUnauthorized) {
        logger.warn("Token invalid (401), clearing auth state");
        removeTokens();
        set({ user: null, isAuthenticated: false, isLoading: false });
      } else {
        logger.warn("API error but keeping token", { status: error?.response?.status });
        set({ isLoading: false });
      }
    }
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));

function initializeAuthState() {
  const token = getToken("ACCESS");
  const currentState = useAuthStore.getState();
  const { user: currentUser, isAuthenticated: currentIsAuthenticated } = currentState;

  const hasTokenAndUser = token && currentUser && currentIsAuthenticated;
  if (hasTokenAndUser) {
    useAuthStore.setState({ isLoading: false });
    return;
  }

  const hasTokenButNotAuthenticated = token && currentUser && !currentIsAuthenticated;
  if (hasTokenButNotAuthenticated) {
    useAuthStore.setState({ isAuthenticated: true, isLoading: false });
    return;
  }

  const hasTokenButNoUser = token && !currentUser;
  if (hasTokenButNoUser) {
    useAuthStore
      .getState()
      .fetchUser()
      .catch(() => {});
    return;
  }

  const hasNoTokenButHasUser = !token && currentUser;
  if (hasNoTokenButHasUser) {
    useAuthStore.getState().setUser(null);
    useAuthStore.setState({ isLoading: false });
    return;
  }

  if (!token && !currentUser) {
    useAuthStore.setState({ isLoading: false });
  }
}

export function useAuth() {
  const store = useAuthStore();
  const { user, isLoading, fetchUser, setUser } = store;
  const hasInitializedOnMount = useRef(false);

  useEffect(() => {
    if (hasInitializedOnMount.current) return;
    hasInitializedOnMount.current = true;
    initializeAuthState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleStorageChange = (e: StorageEvent) => {
      const isTokenChange = e.key === TOKEN_KEYS.ACCESS || e.key === TOKEN_KEYS.REFRESH;
      if (!isTokenChange) return;

      const token = getToken("ACCESS");
      const shouldClearUser = !token && user;
      if (shouldClearUser) {
        setUser(null);
        return;
      }

      const shouldFetchUser = token && !user && !isLoading;
      if (shouldFetchUser) {
        fetchUser();
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [user, isLoading, fetchUser, setUser]);

  return store;
}
