import { apiClient } from "../api/client";

export const healthService = {
  getHealth: async (): Promise<{ status: string }> => {
    const response = await apiClient.get("/health");
    return response.data;
  },
};
