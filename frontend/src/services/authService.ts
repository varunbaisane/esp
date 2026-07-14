import { apiClient } from "../api/client";
import type { RegisterRequest, LoginRequest, TokenResponse, ResetPasswordRequest } from "../types/auth";

export const authService = {
  register: async (data: RegisterRequest) => {
    const response = await apiClient.post("/auth/register", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/login", data);
    return response.data;
  },

  loginWithGoogle: async (idToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/auth/google", { id_token: idToken });
    return response.data;
  },

  me: async () => {
    const response = await apiClient.get("/auth/me");
    return response.data;
  },

  sendVerificationOtp: async (email: string) => {
    const response = await apiClient.post("/auth/send-verification-otp", { email });
    return response.data;
  },

  verifyEmail: async (email: string, otp: string) => {
    const response = await apiClient.post("/auth/verify-email", { email, otp });
    return response.data;
  },

  forgotPassword: async (email: string) => {
    const response = await apiClient.post("/auth/forgot-password", { email });
    return response.data;
  },

  resetPassword: async (data: ResetPasswordRequest) => {
    const response = await apiClient.post("/auth/reset-password", data);
    return response.data;
  },
};
