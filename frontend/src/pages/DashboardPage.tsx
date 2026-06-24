import { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import type { TicketStats } from "../types/ticket";
import { StatsGrid } from "../components/dashboard/StatsGrid";
import { ActivityPreviewCard } from "../components/dashboard/ActivityPreviewCard";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { PageContainer } from "../components/layout/PageContainer";
import type { TicketSummary } from "../types/ticket";
import type { AuditLogSummary } from "../types/audit";
import { activityService } from "../services/activityService";
import { AuthContext } from "../context/AuthContext";
import { useContext } from "react";

export const DashboardPage = () => {
  const authContext = useContext(AuthContext);
  const currentUser = authContext?.currentUser || null;
  const [ticketStats, setTicketStats] = useState<TicketStats | null>(null);
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [recentActivity, setRecentActivity] = useState<AuditLogSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [stats, allTickets, activity] = await Promise.all([
          ticketService.getStats(),
          ticketService.getTickets(),
          activityService.getRecentActivity(10)
        ]);
        setTicketStats(stats);
        setTickets(allTickets);
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

  if (loading) {
    return <LoadingState message="Loading dashboard..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!ticketStats) {
    return null;
  }

  return (
    <PageContainer>
      <div>
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Dashboard</h2>
        <p className="mt-2 text-sm text-gray-500">Overview of current ticket statuses.</p>
      </div>

      <StatsGrid stats={ticketStats} />
      
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-bold text-gray-500 uppercase tracking-wide truncate">My Assigned Tickets</dt>
                  <dd className="mt-2 text-3xl font-black text-indigo-600">
                    {tickets.filter(t => t.assigned_to_id === currentUser?.id && t.status !== "RESOLVED" && t.status !== "CLOSED").length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-bold text-gray-500 uppercase tracking-wide truncate">Unassigned Tickets</dt>
                  <dd className="mt-2 text-3xl font-black text-amber-500">
                    {tickets.filter(t => t.assigned_to_id === null && t.status !== "RESOLVED" && t.status !== "CLOSED").length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8">
        <ActivityPreviewCard logs={recentActivity} isLoading={loading} />
      </div>
    </PageContainer>
  );
};
