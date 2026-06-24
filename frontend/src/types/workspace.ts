import type { TicketSummary } from "./ticket";

export interface WorkspaceStats {
  assigned_tickets: number;
  critical_tickets: number;
  high_priority_tickets: number;
  breached_tickets: number;
}

export interface WorkspaceResponse {
  stats: WorkspaceStats;
  total_assigned_tickets: number;
  tickets: TicketSummary[];
}
