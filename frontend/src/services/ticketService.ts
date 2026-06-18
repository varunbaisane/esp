import { apiClient } from "../api/client";
import type { TicketStats, TicketSummary } from "../types/ticket";

export const ticketService = {
  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<TicketStats>("/tickets/stats");
    return response.data;
  },
  
  getTickets: async (): Promise<TicketSummary[]> => {
    const response = await apiClient.get<TicketSummary[]>("/tickets");
    return response.data;
  }
};
