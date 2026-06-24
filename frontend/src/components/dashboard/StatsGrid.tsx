import type { TicketStats } from "../../types/ticket";
import { StatCard } from "./StatCard";
import { Link } from "react-router-dom";

interface StatsGridProps {
  stats: TicketStats;
}

export const StatsGrid = ({ stats }: StatsGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Link to="/tickets?status=ACTIVE">
        <StatCard 
          title="Open Tickets" 
        value={stats.open_tickets} 
        theme={{ accent: "bg-cyan-400", dot: "bg-cyan-500" }} 
        subtitle="Active" 
      />
      </Link>
      <Link to="/tickets?sla_status=BREACHED">
      <StatCard 
        title="Breached" 
        value={stats.breached_tickets} 
        theme={{ accent: "bg-rose-400", dot: "bg-rose-500" }} 
        subtitle="SLA Overdue" 
      />
      </Link>
      <Link to="/tickets?priority=HIGH&status=ACTIVE">
      <StatCard 
        title="High Priority" 
        value={stats.high_priority_tickets} 
        theme={{ accent: "bg-amber-400", dot: "bg-amber-500" }} 
        subtitle="Important" 
      />
      </Link>
      <Link to="/tickets?priority=CRITICAL&status=ACTIVE">
      <StatCard 
        title="Critical" 
        value={stats.critical_tickets} 
        theme={{ accent: "bg-red-500", dot: "bg-red-600" }} 
        subtitle="Urgent" 
      />
      </Link>
    </div>
  );
};
