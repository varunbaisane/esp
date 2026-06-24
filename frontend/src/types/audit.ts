export type AuditAction =
  | "TICKET_CREATED"
  | "TICKET_UPDATED"
  | "TICKET_ASSIGNED"
  | "TICKET_CLAIMED"
  | "TICKET_REASSIGNED"
  | "TICKET_ESCALATED"
  | "STATUS_CHANGED"
  | "TICKET_RESOLVED"
  | "TICKET_CLOSED";

export type EntityType = "ticket" | "user" | "role";

export interface AuditLogRead {
  id: number;
  ticket_id: number | null;
  actor_id: number;
  actor_name: string;
  actor_email: string;
  action: AuditAction;
  entity_type: EntityType;
  entity_id: string;
  old_value: Record<string, any> | null;
  new_value: Record<string, any> | null;
  event_metadata: Record<string, any> | null;
  created_at: string;
}

export interface AuditLogSummary {
  id: number;
  ticket_id: number | null;
  actor_name: string;
  action: AuditAction;
  entity_type: EntityType;
  entity_id: string;
  event_metadata: Record<string, any> | null;
  created_at: string;
}
