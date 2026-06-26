import { cachedGet } from "../api/client";
import type { AuditLogSummary, AuditLogPaginated } from "../types/audit";

export const activityService = {
  getRecentActivity: async (limit: number = 10): Promise<AuditLogSummary[]> => {
    return cachedGet<AuditLogSummary[]>(`/audit/recent?limit=${limit}`);
  },

  getMyActivity: async (limit: number = 10): Promise<AuditLogSummary[]> => {
    return cachedGet<AuditLogSummary[]>(`/audit/me?limit=${limit}`);
  },

  getActivityFeed: async (limit: number = 25, offset: number = 0): Promise<AuditLogPaginated> => {
    return cachedGet<AuditLogPaginated>(`/audit?limit=${limit}&offset=${offset}`);
  }
};
