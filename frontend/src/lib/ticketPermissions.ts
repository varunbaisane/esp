import type { CurrentUser } from "../types/auth";
import { Roles } from "../types/auth";
import type { TicketRead, TicketStatus } from "../types/ticket";
import type { TicketPermissions } from "../types/permissions";

type TicketAction = 
  | "ASSIGN"
  | "UNASSIGN"
  | "START_PROGRESS"
  | "RESOLVE"
  | "CLOSE"
  | "REOPEN"
  | "CHANGE_PRIORITY"
  | "CHANGE_ASSIGNEE";

interface PermissionMeta {
  allowedRoles: string[];
  requiresAssignee: boolean;
  managerOverride: boolean;
  adminOverride: boolean;
}

const ACTION_PERMISSIONS: Record<TicketAction, PermissionMeta> = {
  ASSIGN: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
  UNASSIGN: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
  START_PROGRESS: {
    allowedRoles: [Roles.SUPPORT_L1, Roles.SUPPORT_L2, Roles.SUPPORT_L3],
    requiresAssignee: true,
    managerOverride: true,
    adminOverride: true,
  },
  RESOLVE: {
    allowedRoles: [Roles.SUPPORT_L1, Roles.SUPPORT_L2, Roles.SUPPORT_L3],
    requiresAssignee: true,
    managerOverride: true,
    adminOverride: true,
  },
  CLOSE: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
  REOPEN: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
  CHANGE_PRIORITY: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
  CHANGE_ASSIGNEE: {
    allowedRoles: [Roles.ENGINEERING_MANAGER, Roles.ADMIN],
    requiresAssignee: false,
    managerOverride: true,
    adminOverride: true,
  },
};

const ALLOWED_TRANSITIONS: Record<TicketStatus, TicketStatus[]> = {
  OPEN: ["IN_PROGRESS"],
  IN_PROGRESS: ["RESOLVED"],
  RESOLVED: ["CLOSED"],
  CLOSED: ["OPEN"],
};

const getUserRoles = (user: CurrentUser | null): Set<string> => {
  if (!user || !user.roles) return new Set();
  return new Set(
    user.roles.map((r) => typeof r === 'string' ? r.toUpperCase() : (r as any).name?.toUpperCase())
  );
};

const ROLE_RANK: Record<string, number> = {
  [Roles.SUPPORT_L1]: 1,
  [Roles.SUPPORT_L2]: 2,
  [Roles.SUPPORT_L3]: 3,
  [Roles.ENGINEERING_MANAGER]: 4,
  [Roles.ADMIN]: 5,
};

const getUserHighestRank = (userRoles: Set<string>): number => {
  let maxRank = 0;
  userRoles.forEach(role => {
    const rank = ROLE_RANK[role] || 0;
    if (rank > maxRank) maxRank = rank;
  });
  return maxRank;
};

const checkTransition = (ticket: TicketRead, newStatus?: TicketStatus): boolean => {
  if (newStatus) {
    if (newStatus === ticket.status) return false;
    return (ALLOWED_TRANSITIONS[ticket.status] || []).includes(newStatus);
  }
  return true;
};

const checkOverride = (userRoles: Set<string>, meta?: PermissionMeta): boolean => {
  if (meta) {
    if (userRoles.has(Roles.ADMIN) && meta.adminOverride) return true;
    if (userRoles.has(Roles.ENGINEERING_MANAGER) && meta.managerOverride) return true;
    return false;
  }
  // No meta: unconditionally grant override to Admin and Manager
  return userRoles.has(Roles.ADMIN) || userRoles.has(Roles.ENGINEERING_MANAGER);
};

const checkRoles = (userRoles: Set<string>, meta: PermissionMeta): boolean => {
  return meta.allowedRoles.some((role) => userRoles.has(role));
};

const checkAssignee = (ticket: TicketRead, user: CurrentUser | null, meta: PermissionMeta): boolean => {
  if (meta.requiresAssignee) {
    if (!user || ticket.assigned_to_id !== user.id) {
      return false;
    }
  }
  return true;
};

const validateAction = (
  user: CurrentUser | null,
  ticket: TicketRead,
  action: TicketAction,
  newStatus?: TicketStatus
): boolean => {
  const meta = ACTION_PERMISSIONS[action];
  if (!meta) return false;

  if (!checkTransition(ticket, newStatus)) return false;

  const userRoles = getUserRoles(user);

  if (checkOverride(userRoles, meta)) return true;
  if (!checkRoles(userRoles, meta)) return false;
  if (!checkAssignee(ticket, user, meta)) return false;

  return true;
};

/**
 * Escalation is not a lifecycle transition — it promotes the ticket's support level.
 * Mirrors backend domain/permissions.py::can_escalate():
 *   - L3 tickets: never escalatable (no next level exists)
 *   - L1 tickets: requires rank >= 1 (any support engineer or above)
 *   - L2 tickets: requires rank >= 2 (L2, L3, Manager, Admin)
 *   - Admin/Manager override: allowed at any valid level
 * NOTE: The backend does NOT require the actor to be the assignee for escalation.
 */
const validateEscalate = (user: CurrentUser | null, ticket: TicketRead): boolean => {
  // 1. Business constraint: L3 has no next level — hard stop before any role check
  if (ticket.support_level === "L3") return false;

  const userRoles = getUserRoles(user);

  // 2. Admin/Manager override (mirrors backend rank >= 4/5)
  if (checkOverride(userRoles)) return true;

  // 3. Rank-based check — mirrors backend can_escalate()
  const userRank = getUserHighestRank(userRoles);
  const requiredRank = ticket.support_level === "L1" ? 1 : ticket.support_level === "L2" ? 2 : 99;

  return userRank >= requiredRank;
};

export const getTicketPermissions = (user: CurrentUser | null, ticket: TicketRead): TicketPermissions => {
  const canAssign = validateAction(user, ticket, "ASSIGN");
  const canChangeAssignee = validateAction(user, ticket, "CHANGE_ASSIGNEE");
  
  const canStartProgress = validateAction(user, ticket, "START_PROGRESS", "IN_PROGRESS");
  const canResolve = validateAction(user, ticket, "RESOLVE", "RESOLVED");
  const canClose = validateAction(user, ticket, "CLOSE", "CLOSED");
  const canReopen = validateAction(user, ticket, "REOPEN", "OPEN");

  const canEditPriority = validateAction(user, ticket, "CHANGE_PRIORITY");
  const canEscalate = validateEscalate(user, ticket);

  return {
    canAssign,
    canChangeAssignee,
    canStartProgress,
    canResolve,
    canClose,
    canReopen,
    canEditPriority,
    canEscalate,
  };
};
