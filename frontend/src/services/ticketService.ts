import { apiClient } from "../api/client";
import type { TicketStats } from "../types/ticket";

export const ticketService = {
  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<TicketStats>("/tickets/stats");
    return response.data;
  },
};
