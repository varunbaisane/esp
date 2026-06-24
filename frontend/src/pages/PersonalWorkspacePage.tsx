import { useEffect, useState } from "react";
import { workspaceService } from "../services/workspaceService";
import type { WorkspaceResponse } from "../types/workspace";
import { MyWorkspaceStats } from "../components/dashboard/MyWorkspaceStats";
import { MyQueueTable } from "../components/dashboard/MyQueueTable";
import { ActivityPreviewCard } from "../components/dashboard/ActivityPreviewCard";
import { activityService } from "../services/activityService";
import type { AuditLogSummary } from "../types/audit";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { PageContainer } from "../components/layout/PageContainer";

export const PersonalWorkspacePage = () => {
  const [workspace, setWorkspace] = useState<WorkspaceResponse | null>(null);
  const [myActivity, setMyActivity] = useState<AuditLogSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [workspaceData, activityData] = await Promise.all([
          workspaceService.getWorkspace(),
          activityService.getMyActivity(10)
        ]);
        setWorkspace(workspaceData);
        setMyActivity(activityData);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message || "Unable to connect to backend.");
        } else {
          setError("Unable to connect to backend.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading personal workspace..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!workspace) {
    return null;
  }

  return (
    <PageContainer>
      <div>
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">My Workspace</h2>
        <p className="mt-2 text-sm text-gray-500">Overview of your assigned workloads and active priorities.</p>
      </div>

      <div className="mt-8">
        <MyWorkspaceStats stats={workspace.stats} />
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">My Queue</h3>
        <MyQueueTable tickets={workspace.tickets} total={workspace.total_assigned_tickets} />
      </div>

      <div className="mt-12">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">My Recent Activity</h3>
        <ActivityPreviewCard logs={myActivity} isLoading={loading} />
      </div>
    </PageContainer>
  );
};
