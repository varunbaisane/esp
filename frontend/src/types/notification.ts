export type NotificationType = 
  | 'TICKET_ASSIGNED'
  | 'TICKET_REASSIGNED'
  | 'TICKET_ESCALATED'
  | 'TICKET_STATUS_CHANGED'
  | 'TICKET_PRIORITY_CHANGED'
  | 'ROLE_ASSIGNED'
  | 'ROLE_REMOVED'
  | 'SYSTEM';

export interface Notification {
  id: number;
  recipient_id: number;
  actor_id: number | null;
  type: NotificationType;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: number | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}
