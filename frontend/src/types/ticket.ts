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
  status: string;
  created_by_id: number;
  assigned_to_id: number | null;
  created_at: string;
  updated_at: string;
}
