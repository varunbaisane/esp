import { Link } from "react-router-dom";
import type { AuditLogSummary } from "../../types/audit";
import { ActivityFeedItem } from "../activity/ActivityFeedItem";
import { Card } from "../common/Card";

interface ActivityPreviewCardProps {
  logs: AuditLogSummary[];
  isLoading: boolean;
}

export const ActivityPreviewCard = ({ logs, isLoading }: ActivityPreviewCardProps) => {
  return (
    <Card>
      <div className="flex items-center justify-between border-b border-gray-100 pb-4 mb-4">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Recent Activity</h2>
          <p className="text-sm text-gray-500 mt-1">Showing latest {logs.length} events</p>
        </div>
        <Link 
          to="/activity" 
          className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 hover:underline flex items-center gap-1"
        >
          View All Activity <span>→</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="text-sm text-gray-500 py-4">Loading activity...</div>
      ) : logs.length === 0 ? (
        <div className="text-sm text-gray-500 py-4 italic">No activity recorded yet.</div>
      ) : (
        <div className="relative border-l-2 border-gray-100 ml-3 space-y-4">
          {logs.map((log) => (
            <ActivityFeedItem key={log.id} log={log} />
          ))}
        </div>
      )}
    </Card>
  );
};
