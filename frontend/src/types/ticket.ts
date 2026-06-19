export type TicketStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
export type TicketFilterStatus = "ALL" | TicketStatus;

export interface TicketStats {
  open: number;
  in_progress: number;
  resolved: number;
  closed: number;
  total: number;
}

export interface TicketSummary {
  id: number;
  title: string;
  description: string | null;
  status: TicketStatus;
  created_by_id: number;
  assigned_to_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface TicketCreate {
  title: string;
  description: string;
  created_by_id: number;
}
