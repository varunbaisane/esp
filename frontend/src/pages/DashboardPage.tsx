import { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import type { TicketStats } from "../types/ticket";
import { StatsGrid } from "../components/dashboard/StatsGrid";
import { RecentActivityCard } from "../components/dashboard/RecentActivityCard";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { PageContainer } from "../components/layout/PageContainer";

export const DashboardPage = () => {
  const [ticketStats, setTicketStats] = useState<TicketStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const stats = await ticketService.getStats();
        setTicketStats(stats);
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
      
      <div className="mt-8">
        <RecentActivityCard />
      </div>
    </PageContainer>
  );
};
