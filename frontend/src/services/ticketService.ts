import { apiClient } from "../api/client";
import type { TicketStats, TicketSummary, TicketCreate, TicketRead, TicketUpdate } from "../types/ticket";

export const ticketService = {
  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<TicketStats>("/tickets/stats");
    return response.data;
  },
  
  getTickets: async (): Promise<TicketSummary[]> => {
    const response = await apiClient.get<TicketSummary[]>("/tickets");
    return response.data;
  },
  
  getTicket: async (id: number): Promise<TicketRead> => {
    const response = await apiClient.get<TicketRead>(`/tickets/${id}`);
    return response.data;
  },

  createTicket: async (data: TicketCreate): Promise<TicketRead> => {
    const response = await apiClient.post<TicketRead>("/tickets", data);
    return response.data;
  },

  updateTicket: async (id: number, data: TicketUpdate): Promise<TicketRead> => {
    const response = await apiClient.patch<TicketRead>(`/tickets/${id}`, data);
    return response.data;
  },

  escalateTicket: async (id: number): Promise<TicketRead> => {
    const response = await apiClient.post<TicketRead>(`/tickets/${id}/escalate`);
    return response.data;
  }
};
