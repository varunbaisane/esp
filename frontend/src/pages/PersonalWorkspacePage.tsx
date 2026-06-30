import { useEffect, useState } from "react";
import { workspaceService } from "../services/workspaceService";
import type { WorkspaceResponse } from "../types/workspace";
import { MyWorkspaceStats } from "../components/dashboard/MyWorkspaceStats";
import { MyQueueTable } from "../components/dashboard/MyQueueTable";
import { ActivityPreviewCard } from "../components/dashboard/ActivityPreviewCard";
import { activityService } from "../services/activityService";
import type { AuditLogSummary } from "../types/audit";
import { StateMessage } from "../components/common/StateMessage";
import { PageContainer } from "../components/layout/PageContainer";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const PersonalWorkspacePage = () => {
  useDocumentTitle("My Workspace");
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

  if (error) {
    return (
      <PageContainer>
        <StateMessage 
          title="Unable to load workspace" 
          message={error} 
          type="error" 
          onRetry={() => window.location.reload()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div>
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">My Workspace</h2>
        <p className="mt-2 text-sm text-gray-500">Overview of your assigned workloads and active priorities.</p>
      </div>

      <div className="mt-8">
        <MyWorkspaceStats stats={workspace?.stats || null} isLoading={loading} />
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">My Queue</h3>
        <MyQueueTable tickets={workspace?.tickets || []} total={workspace?.total_assigned_tickets || 0} isLoading={loading} />
      </div>

      <div className="mt-12">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">My Recent Activity</h3>
        <ActivityPreviewCard logs={myActivity} isLoading={loading} />
      </div>
    </PageContainer>
  );
};
