export interface TicketDistributionStats {
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_level: Record<string, number>;
}

export interface SLAAnalytics {
  total_active: number;
  breached: number;
  healthy: number;
  at_risk: number;
  sla_compliance_percent: number;
}

export interface ResolutionAnalytics {
  average_resolution_hours: number | null;
}

export interface EscalationAnalytics {
  total_escalations: number;
  l1_to_l2: number;
  l2_to_l3: number;
  avg_escalations_per_ticket: number;
}

export interface WorkloadAnalytics {
  max_assigned: number;
  avg_assigned: number;
  unassigned: number;
  workload_distribution: Record<string, number>;
}

export interface AnalyticsResponse {
  distribution: TicketDistributionStats;
  sla: SLAAnalytics;
  resolution: ResolutionAnalytics;
  escalation: EscalationAnalytics;
  workload: WorkloadAnalytics;
  open_vs_closed_ratio: number;
}
