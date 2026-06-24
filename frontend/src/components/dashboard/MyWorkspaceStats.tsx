import type { WorkspaceStats } from "../../types/workspace";
import { StatCard } from "./StatCard";
import { Link } from "react-router-dom";

interface MyWorkspaceStatsProps {
  stats: WorkspaceStats;
}

export const MyWorkspaceStats = ({ stats }: MyWorkspaceStatsProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Link to="/tickets?assigned_to=mine&status=ACTIVE">
        <StatCard 
          title="Assigned To Me" 
          value={stats.assigned_tickets} 
          theme={{ accent: "bg-indigo-400", dot: "bg-indigo-500" }} 
          subtitle="Active Tickets" 
        />
      </Link>
      <Link to="/tickets?assigned_to=mine&status=ACTIVE&priority=CRITICAL">
        <StatCard 
          title="My Critical" 
          value={stats.critical_tickets} 
          theme={{ accent: "bg-red-500", dot: "bg-red-600" }} 
          subtitle="Urgent" 
        />
      </Link>
      <Link to="/tickets?assigned_to=mine&status=ACTIVE&priority=HIGH">
        <StatCard 
          title="My High Priority" 
          value={stats.high_priority_tickets} 
          theme={{ accent: "bg-amber-400", dot: "bg-amber-500" }} 
          subtitle="Important" 
        />
      </Link>
      <Link to="/tickets?assigned_to=mine&sla_status=BREACHED">
        <StatCard 
          title="My Breached" 
          value={stats.breached_tickets} 
          theme={{ accent: "bg-rose-400", dot: "bg-rose-500" }} 
          subtitle="SLA Overdue" 
        />
      </Link>
    </div>
  );
};
