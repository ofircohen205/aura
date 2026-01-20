import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { authApi } from "@/lib/api/auth";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import type { User, TokenResponse, UserLogin, UserRegister } from "@/types/api";

// Mock axios
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

describe("Auth API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("register", () => {
    it("calls register endpoint with correct data", async () => {
      const mockResponse: TokenResponse = {
        access_token: "access_token",
        refresh_token: "refresh_token",
        token_type: "bearer",
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const userData: UserRegister = {
        email: "test@example.com",
        username: "testuser",
        password: "TestPassword123!",
      };

      const result = await authApi.register(userData);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.AUTH.REGISTER, userData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe("login", () => {
    it("calls login endpoint with correct credentials", async () => {
      const mockResponse: TokenResponse = {
        access_token: "access_token",
        refresh_token: "refresh_token",
        token_type: "bearer",
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const credentials: UserLogin = {
        email: "test@example.com",
        password: "TestPassword123!",
      };

      const result = await authApi.login(credentials);

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.AUTH.LOGIN, credentials);
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getCurrentUser", () => {
    it("calls get current user endpoint", async () => {
      const mockUser: User = {
        id: "123",
        email: "test@example.com",
        username: "testuser",
        is_active: true,
        is_verified: true,
        roles: ["user"],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockUser });

      const result = await authApi.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith(ENDPOINTS.AUTH.ME);
      expect(result).toEqual(mockUser);
    });
  });

  describe("updateUser", () => {
    it("calls update user endpoint with correct data", async () => {
      const mockUser: User = {
        id: "123",
        email: "updated@example.com",
        username: "updateduser",
        is_active: true,
        is_verified: true,
        roles: ["user"],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      vi.mocked(apiClient.patch).mockResolvedValue({ data: mockUser });

      const updateData = {
        username: "updateduser",
        email: "updated@example.com",
      };

      const result = await authApi.updateUser(updateData);

      expect(apiClient.patch).toHaveBeenCalledWith(ENDPOINTS.AUTH.ME, updateData);
      expect(result).toEqual(mockUser);
    });
  });

  describe("logout", () => {
    it("calls logout endpoint with refresh token", async () => {
      vi.mocked(apiClient.post).mockResolvedValue({ data: {} });

      await authApi.logout("refresh_token");

      expect(apiClient.post).toHaveBeenCalledWith(ENDPOINTS.AUTH.LOGOUT, {
        refresh_token: "refresh_token",
      });
    });
  });
});
