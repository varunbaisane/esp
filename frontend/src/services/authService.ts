import { apiClient } from "../api/client";
import type { RegisterRequest, LoginRequest, TokenResponse } from "../types/auth";

export const authService = {
  register: async (data: RegisterRequest) => {
    const response = await apiClient.post("/auth/register", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/login", data);
    return response.data;
  },

  me: async () => {
    const response = await apiClient.get("/auth/me");
    return response.data;
  },
};
