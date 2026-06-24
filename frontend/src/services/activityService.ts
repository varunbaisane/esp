import { apiClient } from "../api/client";
import type { AuditLogSummary, AuditLogPaginated } from "../types/audit";

export const activityService = {
  getRecentActivity: async (limit: number = 10): Promise<AuditLogSummary[]> => {
    const response = await apiClient.get<AuditLogSummary[]>(`/audit/recent?limit=${limit}`);
    return response.data;
  },

  getActivityFeed: async (limit: number = 25, offset: number = 0): Promise<AuditLogPaginated> => {
    const response = await apiClient.get<AuditLogPaginated>(`/audit?limit=${limit}&offset=${offset}`);
    return response.data;
  }
};
