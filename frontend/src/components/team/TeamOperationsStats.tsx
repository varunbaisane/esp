import { Link } from "react-router-dom";
import type { TeamOperationsStats as StatsType } from "../../types/teamOperations";

export const TeamOperationsStats = ({ stats }: { stats: StatsType }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Queues (Active) */}
      <div className="flex flex-col gap-4">
        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Active Queues</h4>
        <Link to="/tickets?level=L1&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-indigo-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L1 Queue</dt>
          <dd className="mt-1 text-3xl font-semibold text-indigo-600">{stats.l1_active}</dd>
        </Link>
        <Link to="/tickets?level=L2&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-indigo-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L2 Queue</dt>
          <dd className="mt-1 text-3xl font-semibold text-indigo-600">{stats.l2_active}</dd>
        </Link>
        <Link to="/tickets?level=L3&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-indigo-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L3 Queue</dt>
          <dd className="mt-1 text-3xl font-semibold text-indigo-600">{stats.l3_active}</dd>
        </Link>
      </div>

      {/* Unassigned */}
      <div className="flex flex-col gap-4">
        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Unassigned Work</h4>
        <Link to="/tickets?level=L1&assigned_to=unassigned&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-amber-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L1 Unassigned</dt>
          <dd className="mt-1 text-3xl font-semibold text-amber-500">{stats.l1_unassigned}</dd>
        </Link>
        <Link to="/tickets?level=L2&assigned_to=unassigned&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-amber-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L2 Unassigned</dt>
          <dd className="mt-1 text-3xl font-semibold text-amber-500">{stats.l2_unassigned}</dd>
        </Link>
        <Link to="/tickets?level=L3&assigned_to=unassigned&status=ACTIVE" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-amber-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L3 Unassigned</dt>
          <dd className="mt-1 text-3xl font-semibold text-amber-500">{stats.l3_unassigned}</dd>
        </Link>
      </div>

      {/* Breached */}
      <div className="flex flex-col gap-4">
        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">SLA Risk (Breached)</h4>
        <Link to="/tickets?level=L1&sla_status=BREACHED" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-red-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L1 Breached</dt>
          <dd className="mt-1 text-3xl font-semibold text-red-600">{stats.l1_breached}</dd>
        </Link>
        <Link to="/tickets?level=L2&sla_status=BREACHED" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-red-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L2 Breached</dt>
          <dd className="mt-1 text-3xl font-semibold text-red-600">{stats.l2_breached}</dd>
        </Link>
        <Link to="/tickets?level=L3&sla_status=BREACHED" className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:border-red-500 transition-colors p-5">
          <dt className="text-sm font-medium text-gray-500 truncate">L3 Breached</dt>
          <dd className="mt-1 text-3xl font-semibold text-red-600">{stats.l3_breached}</dd>
        </Link>
      </div>
    </div>
  );
};
