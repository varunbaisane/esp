import type { AuditLogRead } from "../types/audit";

export const getAuditActionText = (log: AuditLogRead): string => {
  switch (log.action) {
    case "TICKET_CREATED":
      return "created ticket";
    case "TICKET_UPDATED":
      return "updated ticket";
    case "TICKET_ASSIGNED":
      return "assigned ticket";
    case "TICKET_REASSIGNED":
      return "reassigned ticket";
    case "TICKET_CLAIMED":
      return "claimed ticket";
    case "TICKET_ESCALATED":
      return "escalated ticket";
    case "STATUS_CHANGED":
      return "changed status";
    case "TICKET_RESOLVED":
      return "resolved ticket";
    case "TICKET_CLOSED":
      return "closed ticket";
    default:
      return (log.action as string).toLowerCase().replace(/_/g, " ");
  }
};

export const renderAuditMetadata = (log: AuditLogRead) => {
  if (!log.event_metadata) return null;
  
  if (log.action === "TICKET_ESCALATED") {
    return <div className="text-xs text-amber-600 font-medium mt-1">{log.event_metadata.from_level} → {log.event_metadata.to_level}</div>;
  }
  
  if (log.action === "STATUS_CHANGED" || log.action === "TICKET_RESOLVED" || log.action === "TICKET_CLOSED") {
    const fromStatus = log.event_metadata.from_status?.replace(/_/g, " ") || log.event_metadata.from_status;
    const toStatus = log.event_metadata.to_status?.replace(/_/g, " ") || log.event_metadata.to_status;
    return <div className="text-xs text-cyan-600 font-medium mt-1">{fromStatus} → {toStatus}</div>;
  }
  
  if (log.action === "TICKET_REASSIGNED") {
    const prevOwner = log.event_metadata.previous_owner || "Unassigned";
    const newOwner = log.event_metadata.new_owner || "Unassigned";
    return (
      <div className="text-xs text-indigo-600 font-medium mt-1">
        <span className="block text-gray-400">Assigned To:</span>
        {prevOwner} → {newOwner}
      </div>
    );
  }
  
  if (log.action === "TICKET_CLAIMED") {
    const newOwner = log.event_metadata.new_owner || log.actor_name;
    return (
      <div className="text-xs text-indigo-600 font-medium mt-1">
        <span className="block text-gray-400">Assigned To:</span>
        {newOwner}
      </div>
    );
  }
  
  return null;
};
