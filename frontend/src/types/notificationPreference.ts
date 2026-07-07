export type NotificationChannel = "IN_APP" | "EMAIL" | "BROWSER";

export type NotificationType =
  | "WELCOME"
  | "TICKET_ASSIGNED"
  | "TICKET_REASSIGNED"
  | "TICKET_STATUS_CHANGED"
  | "TICKET_PRIORITY_CHANGED"
  | "ROLE_ASSIGNED"
  | "ROLE_REMOVED"
  | "FIRST_ROLE_ASSIGNED";

export interface NotificationPreference {
  id: number;
  notification_type: NotificationType;
  channel: NotificationChannel;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferenceUpdate {
  enabled: boolean;
}
