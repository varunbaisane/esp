import { useEffect, useState } from "react";
import { teamOperationsService } from "../services/teamOperationsService";
import type { TeamOperationsResponse } from "../types/teamOperations";
import { TeamOperationsStats } from "../components/team/TeamOperationsStats";
import { WorkloadTable } from "../components/team/WorkloadTable";
import { StateMessage } from "../components/common/StateMessage";
import { PageContainer } from "../components/layout/PageContainer";
import { Card } from "../components/common/Card";
import { TableSkeleton } from "../components/common/TableSkeleton";

export const TeamOperationsPage = () => {
  const [data, setData] = useState<TeamOperationsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const responseData = await teamOperationsService.getTeamOperations();
        setData(responseData);
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
          title="Unable to load team operations" 
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
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Team Operations</h2>
        <p className="mt-2 text-sm text-gray-500">Monitor queue health, unassigned work, and team workload distribution.</p>
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">Operational Queues</h3>
        <TeamOperationsStats stats={data?.stats || null} isLoading={loading} />
      </div>

      <div className="mt-12">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">Engineer Workloads</h3>
        <Card noPadding>
          {loading || !data ? (
            <TableSkeleton rows={5} />
          ) : (
            <WorkloadTable workloads={data.workloads} />
          )}
        </Card>
      </div>
    </PageContainer>
  );
};
