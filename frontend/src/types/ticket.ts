export type TicketStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type TicketLevel = "L1" | "L2" | "L3";
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
  status: TicketStatus;
  priority: TicketPriority;
  support_level: TicketLevel;
  created_by_id: number;
  assigned_to_id: number | null;
  created_at: string;
}

export interface TicketRead {
  id: number;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  support_level: TicketLevel;
  created_by_id: number;
  created_by_name: string;
  assigned_to_id: number | null;
  assigned_to_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface TicketCreate {
  title: string;
  description: string;
  priority: TicketPriority;
}

export interface TicketUpdate {
  status?: TicketStatus;
  priority?: TicketPriority;
  assigned_to_id?: number | null;
}
