import { useEffect, useState } from "react";
import { getTicketAudit } from "../../api/auditService";
import type { AuditLogRead } from "../../types/audit";
import { Card } from "../common/Card";
import { getAuditActionText, renderAuditMetadata } from "../../utils/auditFormatting";
import { UserAvatar } from "../common/UserAvatar";
import { TimelineSkeleton } from "../common/TimelineSkeleton";
import { formatRelativeDateTime } from "../../lib/dateTime";

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
    return (
      <Card>
        <TimelineSkeleton />
      </Card>
    );
  }

  if (logs.length === 0) {
    return null;
  }

  if (logs.length === 0) {
    return null;
  }

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
              <span className="text-xs text-gray-400 font-medium whitespace-nowrap">
                {formatRelativeDateTime(log.created_at)}
              </span>
              <div className="text-sm text-gray-800 flex items-center gap-2">
                <UserAvatar name={log.actor_name} size="sm" />
                <span>
                  <span className="font-semibold text-gray-900">{log.actor_name}</span> {getAuditActionText(log)}
                </span>
              </div>
              <div className="mt-1">
                {renderAuditMetadata(log)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
