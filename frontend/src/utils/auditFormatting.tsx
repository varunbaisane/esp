import React from "react";
import type { AuditLogRead } from "../types/audit";
import { getPriorityTextColor } from "../components/tickets/TicketPriorityBadge";

export const getAuditActionText = (log: AuditLogRead): React.ReactNode => {
  switch (log.action) {
    case "TICKET_CREATED":
      return "created the ticket";
    case "TICKET_UPDATED": {
      if (log.event_metadata?.field) {
        const field = log.event_metadata.field.toLowerCase();
        if (field === "priority" || field === "assignee") {
          return `changed the ${field}`;
        }
        return `updated the ${field}`;
      }
      return "updated the ticket";
    }
    case "TICKET_ASSIGNED": {
      const assignee = log.event_metadata?.new_owner;
      return assignee ? (
        <>
          assigned the ticket to <span className="font-semibold text-gray-900">{assignee}</span>
        </>
      ) : (
        "assigned the ticket"
      );
    }
    case "TICKET_REASSIGNED":
      return "reassigned the ticket";
    case "TICKET_CLAIMED":
      return "claimed the ticket";
    case "TICKET_ESCALATED":
      return "escalated the ticket";
    case "STATUS_CHANGED":
      return "changed the ticket status";
    case "TICKET_RESOLVED":
      return "resolved the ticket";
    case "TICKET_CLOSED":
      return "closed the ticket";
    default:
      return (log.action as string).toLowerCase().replace(/_/g, " ");
  }
};

export const renderAuditMetadata = (log: AuditLogRead) => {
  if (!log.event_metadata) return null;

  if (log.action === "TICKET_UPDATED") {
    const { field, old_value, new_value } = log.event_metadata;
    if (field === "priority" && old_value && new_value) {
      return (
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs font-semibold ${getPriorityTextColor(old_value as any)}`}>{old_value}</span>
          <span className="text-gray-400 text-xs font-medium">→</span>
          <span className={`text-xs font-semibold ${getPriorityTextColor(new_value as any)}`}>{new_value}</span>
        </div>
      );
    }
    if (field === "assignee" && old_value && new_value) {
      return (
        <div className="text-xs text-indigo-600 font-medium mt-1">
          {old_value} → {new_value}
        </div>
      );
    }
  }

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
        {prevOwner} → {newOwner}
      </div>
    );
  }

  // TICKET_ASSIGNED metadata display is handled in the text itself based on the spec
  // "assigned the ticket to Mike Wazowski"

  if (log.action === "TICKET_CLAIMED") {
    // Only show if it's different or just rely on the text? "claimed the ticket" is usually enough.
    // The previous implementation showed "Assigned To: ...". We'll keep it simple if it's redundant.
    return null;
  }

  return null;
};
