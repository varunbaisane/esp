import { cachedGet } from "../api/client";
import type { AnalyticsResponse } from "../types/analytics";

export const analyticsService = {
  getAnalytics: async (): Promise<AnalyticsResponse> => {
    return cachedGet<AnalyticsResponse>("/analytics");
  },
};
