import { apiClient } from "./client";
import type { User, TokenResponse, UserRegister, UserLogin, UserUpdate } from "@/types/api";

export const authApi = {
  register: async (data: UserRegister): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/register", data);
    return response.data;
  },

  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/login", data);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  updateUser: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<User>("/auth/me", data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
  },
};
