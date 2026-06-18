import type { TicketStats } from "../../types/ticket";
import { StatCard } from "./StatCard";

interface StatsGridProps {
  stats: TicketStats;
}

export const StatsGrid = ({ stats }: StatsGridProps) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
      <StatCard title="Total" value={stats.total} />
      <StatCard title="Open" value={stats.open} />
      <StatCard title="In Progress" value={stats.in_progress} />
      <StatCard title="Resolved" value={stats.resolved} />
      <StatCard title="Closed" value={stats.closed} />
    </div>
  );
};
