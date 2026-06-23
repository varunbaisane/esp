export type TicketStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type TicketLevel = "L1" | "L2" | "L3";
export type SLAStatus = "HEALTHY" | "AT_RISK" | "BREACHED";
export type TicketFilterStatus = "ALL" | TicketStatus;

export interface TicketStats {
  open_tickets: number;
  breached_tickets: number;
  high_priority_tickets: number;
  critical_tickets: number;
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
  sla_due_at: string;
  is_sla_breached: boolean;
  sla_status: SLAStatus;
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
  sla_due_at: string;
  is_sla_breached: boolean;
  sla_status: SLAStatus;
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
