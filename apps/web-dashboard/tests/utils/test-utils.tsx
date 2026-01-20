import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { useAuthStore } from "@/lib/hooks/useAuth";
import type { User } from "@/types/api";

// Mock user for testing
export const mockUser: User = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  email: "test@example.com",
  username: "testuser",
  is_active: true,
  is_verified: true,
  roles: ["user"],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

interface AllTheProvidersProps {
  children: React.ReactNode;
  initialAuthState?: {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
  };
}

function AllTheProviders({ children, initialAuthState }: AllTheProvidersProps) {
  // Set initial auth state if provided
  if (initialAuthState) {
    useAuthStore.setState(initialAuthState);
  }

  return <>{children}</>;
}

interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  initialAuthState?: {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
  };
}

export function renderWithProviders(
  ui: ReactElement,
  { initialAuthState, ...renderOptions }: CustomRenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <AllTheProviders initialAuthState={initialAuthState}>{children}</AllTheProviders>;
  }

  return { ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

export * from "@testing-library/react";
export { renderWithProviders as render };
