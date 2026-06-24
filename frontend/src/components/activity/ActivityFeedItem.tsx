import { Link } from "react-router-dom";
import type { AuditLogSummary } from "../../types/audit";
import { getAuditActionText, renderAuditMetadata } from "../../utils/auditFormatting";
import { UserAvatar } from "../common/UserAvatar";

interface ActivityFeedItemProps {
  log: AuditLogSummary;
}

export const ActivityFeedItem = ({ log }: ActivityFeedItemProps) => {
  return (
    <div className="relative pl-6 py-2">
      <div className="absolute w-3 h-3 bg-white border-2 border-indigo-400 rounded-full -left-[7px] top-3.5" />
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-gray-800 flex items-center gap-2">
            <UserAvatar name={log.actor_name} size="sm" />
            <span>
              <span className="font-semibold text-gray-900">{log.actor_name}</span> {getAuditActionText(log as any)}
              {log.ticket_id && (
                <span className="ml-1">
                  ticket <Link to={`/tickets/${log.ticket_id}`} className="text-indigo-600 font-semibold hover:text-indigo-700 hover:underline">#{log.ticket_id}</Link>
                </span>
              )}
            </span>
          </div>
          <span className="text-xs text-gray-400 font-medium whitespace-nowrap">
            {new Intl.DateTimeFormat('en-US', { 
              month: 'short',
              day: 'numeric',
              hour: 'numeric', 
              minute: 'numeric', 
              hour12: true 
            }).format(new Date(log.created_at))}
          </span>
        </div>
        {renderAuditMetadata(log as any)}
      </div>
    </div>
  );
};
