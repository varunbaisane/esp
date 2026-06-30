import { useEffect, useState } from "react";
import { PageContainer } from "../components/layout/PageContainer";
import { ActivityFeed } from "../components/activity/ActivityFeed";
import { PaginationControls } from "../components/activity/PaginationControls";
import { activityService } from "../services/activityService";
import type { AuditLogSummary } from "../types/audit";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const ActivityPage = () => {
  useDocumentTitle("Activity");
  const [logs, setLogs] = useState<AuditLogSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const limit = 25;

  useEffect(() => {
    const fetchFeed = async () => {
      setIsLoading(true);
      try {
        const offset = (currentPage - 1) * limit;
        const data = await activityService.getActivityFeed(limit, offset);
        setLogs(data.items);
        setTotal(data.total);
      } catch (err) {
        console.error("Failed to fetch activity feed:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFeed();
  }, [currentPage]);

  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <PageContainer>
      <div>
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Activity</h2>
        <p className="mt-2 text-sm text-gray-500">Browse operational history across the platform.</p>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-6">
          <ActivityFeed logs={logs} isLoading={isLoading} />
        </div>
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          isLoading={isLoading}
        />
      </div>
    </PageContainer>
  );
};
