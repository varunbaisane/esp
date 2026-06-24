export interface EngineerWorkload {
  user_id: number;
  full_name: string;
  role: string;
  assigned_tickets: number;
  critical_tickets: number;
  breached_tickets: number;
}

export interface TeamOperationsStats {
  l1_active: number;
  l2_active: number;
  l3_active: number;

  l1_unassigned: number;
  l2_unassigned: number;
  l3_unassigned: number;

  l1_breached: number;
  l2_breached: number;
  l3_breached: number;
}

export interface TeamOperationsResponse {
  stats: TeamOperationsStats;
  workloads: EngineerWorkload[];
}
