import { useEffect, useState } from "react";
import { getTicketAudit } from "../../api/auditService";
import type { AuditLogRead } from "../../types/audit";
import { Card } from "../common/Card";

interface AuditTimelineProps {
  ticketId: number;
}

export const AuditTimeline = ({ ticketId }: AuditTimelineProps) => {
  const [logs, setLogs] = useState<AuditLogRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const data = await getTicketAudit(ticketId);
        setLogs(data);
      } catch (error) {
        console.error("Failed to fetch audit logs", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAudit();
  }, [ticketId]);

  if (isLoading) {
    return <div className="text-sm text-gray-500 p-4">Loading timeline...</div>;
  }

  if (logs.length === 0) {
    return null;
  }

  const formatAction = (log: AuditLogRead) => {
    switch (log.action) {
      case "TICKET_CREATED":
        return "created ticket";
      case "TICKET_UPDATED":
        return "updated ticket";
      case "TICKET_ASSIGNED":
        return "assigned ticket";
      case "TICKET_REASSIGNED":
        return "reassigned ticket";
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

  const renderDetails = (log: AuditLogRead) => {
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

  return (
    <Card>
      <h3 className="text-xs font-bold text-gray-400 mb-6 uppercase tracking-widest border-b border-gray-100 pb-2">
        Activity Timeline
      </h3>
      <div className="relative border-l-2 border-gray-100 ml-3 space-y-6">
        {logs.map((log) => (
          <div key={log.id} className="relative pl-6">
            <div className="absolute w-3 h-3 bg-white border-2 border-indigo-400 rounded-full -left-[7px] top-1.5" />
            <div className="flex flex-col gap-0.5">
              <span className="text-xs text-gray-400 font-medium">
                {new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: 'numeric', hour12: true }).format(new Date(log.created_at))}
              </span>
              <div className="text-sm text-gray-800">
                <span className="font-semibold text-gray-900">{log.actor_name}</span> {formatAction(log)}
              </div>
              {renderDetails(log)}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
