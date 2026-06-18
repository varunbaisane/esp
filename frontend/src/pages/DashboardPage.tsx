import { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import type { TicketStats } from "../types/ticket";
import { StatsGrid } from "../components/dashboard/StatsGrid";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";

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
      } catch (err: any) {
        setError(err.message || "Unable to connect to backend.");
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
    <div className="space-y-6">
      <div className="pb-2">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard Overview</h2>
      </div>

      <StatsGrid stats={ticketStats} />
    </div>
  );
};
