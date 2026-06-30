import type { CurrentUser } from "../types/auth";
import type { TicketLevel } from "../types/ticket";

import { Roles } from "../types/auth";

const ROLE_RANK: Record<string, number> = {
  [Roles.SUPPORT_L1]: 1,
  [Roles.SUPPORT_L2]: 2,
  [Roles.SUPPORT_L3]: 3,
  [Roles.ENGINEERING_MANAGER]: 4,
  [Roles.ADMIN]: 5,
};

export const getUserHighestRank = (user: { roles?: (string | { name: string })[] } | null): number => {
  if (!user || !user.roles || user.roles.length === 0) return 0;
  return Math.max(...user.roles.map(role => {
    const roleName = typeof role === 'string' ? role : role.name;
    return ROLE_RANK[roleName] || 0;
  }));
};

export const canEscalateTicket = (user: CurrentUser | null, currentLevel: TicketLevel): boolean => {
  const userRank = getUserHighestRank(user);
  
  if (currentLevel === "L1") {
    return userRank >= 1;
  }
  
  if (currentLevel === "L2") {
    return userRank >= 2;
  }
  
  if (currentLevel === "L3") {
    // Cannot escalate past L3
    return false;
  }
  
  return false;
};

export const canAssignTicket = (user: CurrentUser | null, ticketLevel: TicketLevel): boolean => {
  const userRank = getUserHighestRank(user);
  
  if (userRank >= 4) return true; // Manager/Admin can assign anything
  
  if (ticketLevel === "L1" && userRank >= 1) return true;
  if (ticketLevel === "L2" && userRank >= 2) return true;
  if (ticketLevel === "L3" && userRank >= 3) return true;
  
  return false;
};

export const canClaimTicket = (user: CurrentUser | null, ticketLevel: TicketLevel): boolean => {
  const userRank = getUserHighestRank(user);
  
  if (userRank >= 4) return true; // Manager/Admin can claim anything
  
  if (ticketLevel === "L1" && userRank >= 1) return true;
  if (ticketLevel === "L2" && userRank >= 2) return true;
  if (ticketLevel === "L3" && userRank >= 3) return true;
  
  return false;
};
