import type { TicketStats } from "../../types/ticket";
import { StatCard } from "./StatCard";

interface StatsGridProps {
  stats: TicketStats;
}

export const StatsGrid = ({ stats }: StatsGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard title="Open" value={stats.open} status="OPEN" subtitle="Active" />
      <StatCard title="In Progress" value={stats.in_progress} status="IN_PROGRESS" subtitle="Active" />
      <StatCard title="Resolved" value={stats.resolved} status="RESOLVED" subtitle="Completed" />
      <StatCard title="Closed" value={stats.closed} status="CLOSED" subtitle="Archived" />
    </div>
  );
};
