import { apiClient } from "../api/client";
import type { AnalyticsResponse } from "../types/analytics";

export const analyticsService = {
  getAnalytics: async (): Promise<AnalyticsResponse> => {
    const response = await apiClient.get<AnalyticsResponse>("/analytics");
    return response.data;
  },
};
