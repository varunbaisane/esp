import type { CurrentUser } from "../types/auth";
import type { TicketLevel } from "../types/ticket";

const ROLE_RANK: Record<string, number> = {
  "SUPPORT_L1": 1,
  "SUPPORT_L2": 2,
  "SUPPORT_L3": 3,
  "ENGINEERING_MANAGER": 4,
  "ADMIN": 5,
};

export const getUserHighestRank = (user: CurrentUser | null): number => {
  if (!user || !user.roles || user.roles.length === 0) return 0;
  return Math.max(...user.roles.map(role => ROLE_RANK[role] || 0));
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
