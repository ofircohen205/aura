import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { logger } from "@/lib/utils/logger";
import { navigateTo } from "@/lib/utils/navigation";
import { getEnv } from "@/lib/utils/env";
import { ROUTES } from "@/lib/routes";
import { ENDPOINTS } from "./endpoints";

const API_BASE_URL = getEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");
const AURA_CLIENT = "web-dashboard";

interface QueuedRequest {
  resolve: (value: any) => void;
  reject: (error: any) => void;
}

class ApiClient {
  private client: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: QueuedRequest[] = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
        "X-Aura-Client": AURA_CLIENT,
      },
      withCredentials: true,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (config.headers) {
          config.headers["X-Aura-Client"] = AURA_CLIENT;
        }

        if (typeof window !== "undefined") {
          const token = localStorage.getItem("access_token");
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }

          const csrfToken = this.getCsrfToken();
          const isStateChangingMethod =
            config.method &&
            ["post", "put", "patch", "delete"].includes(config.method.toLowerCase());
          if (csrfToken && config.headers && isStateChangingMethod) {
            config.headers["X-CSRF-Token"] = csrfToken;
          }
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            try {
              const token = await this.waitForTokenRefresh();
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              return await this.client(originalRequest);
            } catch (err) {
              return Promise.reject(err);
            }
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = localStorage.getItem("refresh_token");
            if (!refreshToken) {
              throw new Error("No refresh token available");
            }

            const response = await axios.post(
              `${API_BASE_URL}${ENDPOINTS.AUTH.REFRESH}`,
              { refresh_token: refreshToken },
              {
                withCredentials: true,
                headers: {
                  "X-Aura-Client": AURA_CLIENT,
                },
              }
            );

            const { access_token, refresh_token: newRefreshToken } = response.data;
            localStorage.setItem("access_token", access_token);
            if (newRefreshToken) {
              localStorage.setItem("refresh_token", newRefreshToken);
            }

            this.processQueue(access_token);

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }

            return await this.client(originalRequest);
          } catch (refreshError) {
            this.processQueue(null, refreshError);
            logger.error("Token refresh failed", refreshError, {
              endpoint: originalRequest.url,
            });

            if (typeof window !== "undefined") {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              navigateTo(ROUTES.AUTH.LOGIN);
            }
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private waitForTokenRefresh(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.failedQueue.push({ resolve, reject });
    });
  }

  private processQueue(token: string | null, error?: unknown) {
    this.failedQueue.forEach(promise => {
      if (token) {
        promise.resolve(token);
      } else {
        promise.reject(error || new Error("Token refresh failed"));
      }
    });
    this.failedQueue = [];
  }

  private getCsrfToken(): string | null {
    if (typeof document === "undefined") return null;
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=");
      if (name === "csrf-token") {
        return decodeURIComponent(value);
      }
    }
    return null;
  }

  get instance(): AxiosInstance {
    return this.client;
  }
}

export const apiClient = new ApiClient().instance;
