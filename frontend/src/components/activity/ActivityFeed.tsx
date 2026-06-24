import type { AuditLogSummary } from "../../types/audit";
import { ActivityFeedItem } from "./ActivityFeedItem";

interface ActivityFeedProps {
  logs: AuditLogSummary[];
  isLoading: boolean;
}

export const ActivityFeed = ({ logs, isLoading }: ActivityFeedProps) => {
  if (isLoading) {
    return <div className="text-sm text-gray-500 py-4">Loading activity...</div>;
  }

  if (logs.length === 0) {
    return <div className="text-sm text-gray-500 py-4 italic">No activity recorded yet.</div>;
  }

  return (
    <div className="relative border-l-2 border-gray-100 ml-3 space-y-4">
      {logs.map((log) => (
        <ActivityFeedItem key={log.id} log={log} />
      ))}
    </div>
  );
};
