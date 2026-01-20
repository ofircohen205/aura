import { apiClient } from "./client";
import { ENDPOINTS } from "./endpoints";
import type { User, TokenResponse, UserRegister, UserLogin, UserUpdate } from "@/types/api";

export const authApi = {
  register: async (data: UserRegister): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(ENDPOINTS.AUTH.REGISTER, data);
    return response.data;
  },

  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(ENDPOINTS.AUTH.LOGIN, data);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(ENDPOINTS.AUTH.REFRESH, {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>(ENDPOINTS.AUTH.ME);
    return response.data;
  },

  updateUser: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<User>(ENDPOINTS.AUTH.ME, data);
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post(ENDPOINTS.AUTH.LOGOUT, {
      refresh_token: refreshToken,
    });
  },
};
