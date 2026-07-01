import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRecentAudit } from "../../api/auditService";
import type { AuditLogSummary } from "../../types/audit";
import { Card } from "../common/Card";
import { formatRelativeDateTime } from "../../lib/dateTime";

import { getAuditActionText, renderAuditMetadata } from "../../utils/auditFormatting";

export const RecentActivityCard = () => {
  const [logs, setLogs] = useState<AuditLogSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const data = await getRecentAudit(10);
        setLogs(data);
      } catch (error) {
        console.error("Failed to fetch recent audit logs", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAudit();
  }, []);

  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900 tracking-tight">Recent Activity</h3>
      </div>
      
      {logs.length === 0 ? (
        <p className="text-sm text-gray-500 italic">No recent activity.</p>
      ) : (
        <div className="space-y-4">
          {logs.map((log) => (
            <div key={log.id} className="flex items-start gap-3 border-b border-gray-50 pb-3 last:border-0 last:pb-0">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                <span className="text-xs font-bold text-indigo-700">
                  {log.actor_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex flex-col min-w-0">
                <div className="text-sm text-gray-800">
                  <span className="font-semibold text-gray-900">{log.actor_name}</span>{" "}
                  {getAuditActionText(log as any)}{" "}
                  {log.entity_type === "ticket" && log.ticket_id && (
                    <Link to={`/tickets/${log.ticket_id}`} className="font-medium text-indigo-600 hover:text-indigo-800">
                      #{log.ticket_id}
                    </Link>
                  )}
                </div>
                {renderAuditMetadata(log as any)}
                <span className="text-xs text-gray-400 whitespace-nowrap mt-0.5">
                  {formatRelativeDateTime(log.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
