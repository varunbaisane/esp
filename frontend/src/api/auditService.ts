import { apiClient } from "./client";
import type { AuditLogRead, AuditLogSummary } from "../types/audit";

export const getTicketAudit = async (ticketId: number): Promise<AuditLogRead[]> => {
  const response = await apiClient.get<AuditLogRead[]>(`/audit/tickets/${ticketId}`);
  return response.data;
};

export const getRecentAudit = async (limit: number = 50): Promise<AuditLogSummary[]> => {
  const response = await apiClient.get<AuditLogSummary[]>("/audit/recent", {
    params: { limit },
  });
  return response.data;
};
