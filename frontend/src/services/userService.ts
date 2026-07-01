import { apiClient } from "../api/client";
import type { UserSummaryResponse, RoleOperationRequest } from "../types/user";

export const userService = {
  getUsers: async (params?: { search?: string; status?: string; role?: string }): Promise<UserSummaryResponse[]> => {
    const response = await apiClient.get<UserSummaryResponse[]>("/users", { params });
    return response.data;
  },

  operateUserRole: async (userId: number, data: RoleOperationRequest): Promise<{status: string}> => {
    const response = await apiClient.patch<{status: string}>(`/users/${userId}/roles`, data);
    return response.data;
  }
};
