import type { TicketStats } from "../../types/ticket";
import { StatCard } from "./StatCard";

interface StatsGridProps {
  stats: TicketStats;
}

export const StatsGrid = ({ stats }: StatsGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard 
        title="Open Tickets" 
        value={stats.open_tickets} 
        theme={{ accent: "bg-cyan-400", dot: "bg-cyan-500" }} 
        subtitle="Active" 
      />
      <StatCard 
        title="Breached" 
        value={stats.breached_tickets} 
        theme={{ accent: "bg-rose-400", dot: "bg-rose-500" }} 
        subtitle="SLA Overdue" 
      />
      <StatCard 
        title="High Priority" 
        value={stats.high_priority_tickets} 
        theme={{ accent: "bg-amber-400", dot: "bg-amber-500" }} 
        subtitle="Important" 
      />
      <StatCard 
        title="Critical" 
        value={stats.critical_tickets} 
        theme={{ accent: "bg-red-500", dot: "bg-red-600" }} 
        subtitle="Urgent" 
      />
    </div>
  );
};
