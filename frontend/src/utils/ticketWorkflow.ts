import type { TicketStatus } from "../types/ticket";

export const ALLOWED_TRANSITIONS: Record<TicketStatus, TicketStatus[]> = {
  OPEN: ["IN_PROGRESS"],
  IN_PROGRESS: ["RESOLVED"],
  RESOLVED: ["CLOSED", "IN_PROGRESS"],
  CLOSED: ["IN_PROGRESS"],
};

export const getValidNextStates = (currentStatus: TicketStatus): TicketStatus[] => {
  return ALLOWED_TRANSITIONS[currentStatus] || [];
};
