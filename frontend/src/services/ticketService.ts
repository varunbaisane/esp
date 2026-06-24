import { apiClient } from "../api/client";
import type { TicketStats, TicketCreate, TicketRead, TicketUpdate, TicketPaginated, TicketFilters } from "../types/ticket";

export const ticketService = {
  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<TicketStats>("/tickets/stats");
    return response.data;
  },
  
  getTickets: async (filters: TicketFilters = {}, limit: number = 25, offset: number = 0, sortBy: string = "created_at", sortOrder: string = "desc"): Promise<TicketPaginated> => {
    const params = new URLSearchParams();
    
    if (filters.status && filters.status !== "ALL") params.append("status", filters.status);
    if (filters.priority && filters.priority !== "ALL") params.append("priority", filters.priority);
    if (filters.level && filters.level !== "ALL") params.append("level", filters.level);
    if (filters.assigned_to && filters.assigned_to !== "ALL") params.append("assigned_to", filters.assigned_to);
    if (filters.sla_status && filters.sla_status !== "ALL") params.append("sla_status", filters.sla_status);
    
    params.append("sort_by", sortBy);
    params.append("sort_order", sortOrder);
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());

    const response = await apiClient.get<TicketPaginated>(`/tickets?${params.toString()}`);
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
  },

  claimTicket: async (id: number): Promise<TicketRead> => {
    const response = await apiClient.post<TicketRead>(`/tickets/${id}/claim`);
    return response.data;
  },

  assignTicket: async (id: number, assigneeId: number): Promise<TicketRead> => {
    const response = await apiClient.post<TicketRead>(`/tickets/${id}/assign`, {
      assignee_id: assigneeId
    });
    return response.data;
  }
};
