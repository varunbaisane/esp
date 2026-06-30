import { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import type { TicketStats } from "../types/ticket";
import { StatsGrid } from "../components/dashboard/StatsGrid";
import { ActivityPreviewCard } from "../components/dashboard/ActivityPreviewCard";
import { StateMessage } from "../components/common/StateMessage";
import { CardSkeleton } from "../components/common/CardSkeleton";
import { PageContainer } from "../components/layout/PageContainer";
import { activityService } from "../services/activityService";
import type { AuditLogSummary } from "../types/audit";
import { Link } from "react-router-dom";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const DashboardPage = () => {
  useDocumentTitle("Global Operations");
  const [ticketStats, setTicketStats] = useState<TicketStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<AuditLogSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [stats, activity] = await Promise.all([
          ticketService.getStats(),
          activityService.getRecentActivity(10)
        ]);
        setTicketStats(stats);
        setRecentActivity(activity);
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
          title="Unable to load dashboard" 
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
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Global Operations</h2>
        <p className="mt-2 text-sm text-gray-500">Overview of system-wide ticket queues and performance.</p>
      </div>

      <div className="mt-8">
        <StatsGrid stats={ticketStats} isLoading={loading} />
      
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
        {loading || !ticketStats ? (
          <>
            <CardSkeleton />
            <CardSkeleton />
          </>
        ) : (
          <>
            <Link to="/tickets?assigned_to=mine&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-indigo-500 transition-colors">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-bold text-gray-500 uppercase tracking-wide truncate">My Assigned Tickets</dt>
                      <dd className="mt-2 text-3xl font-black text-indigo-600">
                        {ticketStats.my_assigned_tickets}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>

            <Link to="/tickets?assigned_to=unassigned&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-amber-500 transition-colors">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-bold text-gray-500 uppercase tracking-wide truncate">Unassigned Tickets</dt>
                      <dd className="mt-2 text-3xl font-black text-amber-500">
                        {ticketStats.unassigned_tickets}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>
          </>
        )}
      </div>
      </div>
      
      <div className="mt-12">
        <h3 className="text-xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">Recent Activity</h3>
        <ActivityPreviewCard logs={recentActivity} isLoading={loading} />
      </div>
    </PageContainer>
  );
};
