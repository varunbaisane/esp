export interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
  roles?: { name: string }[];
}

export interface RoleData {
  code: string;
  display_name: string;
}

export interface UserSummaryResponse {
  id: number;
  name: string;
  email: string;
  account_status: 'PENDING_APPROVAL' | 'ACTIVE' | 'DISABLED';
  current_role: RoleData | null;
  joined_at: string;
  last_login_at: string | null;
  assignable_roles: string[];
}

export const RoleOperation = {
  ASSIGN: 'assign',
  REMOVE: 'remove'
} as const;

export type RoleOperation = typeof RoleOperation[keyof typeof RoleOperation];

export interface RoleOperationRequest {
  operation: RoleOperation;
  role_code: string;
}
