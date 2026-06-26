import { Card } from "../common/Card";
import type { AnalyticsResponse } from "../../types/analytics";
import { CardSkeleton } from "../common/CardSkeleton";

interface AnalyticsSummaryProps {
  analytics: AnalyticsResponse | null;
  isLoading?: boolean;
}

export const AnalyticsSummary = ({ analytics, isLoading }: AnalyticsSummaryProps) => {
  if (isLoading || !analytics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {Array.from({ length: 5 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
      <Card className="flex flex-col">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">SLA Compliance</h3>
        <div className="mt-2 text-3xl font-bold text-emerald-600">
          {analytics.sla.sla_compliance_percent}%
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Across {analytics.sla.total_active} active tickets
        </p>
      </Card>

      <Card className="flex flex-col">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Avg Resolution</h3>
        <div className="mt-2 text-3xl font-bold text-gray-900">
          {analytics.resolution.average_resolution_hours !== null 
            ? `${analytics.resolution.average_resolution_hours}h` 
            : "N/A"}
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Historical average
        </p>
      </Card>

      <Card className="flex flex-col">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Total Escalations</h3>
        <div className="mt-2 text-3xl font-bold text-gray-900">
          {analytics.escalation.total_escalations}
        </div>
        <p className="mt-1 text-xs text-gray-400">
          {analytics.escalation.avg_escalations_per_ticket} avg / ticket
        </p>
      </Card>

      <Card className="flex flex-col">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Unassigned</h3>
        <div className="mt-2 text-3xl font-bold text-amber-600">
          {analytics.workload.unassigned}
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Requires assignment
        </p>
      </Card>

      <Card className="flex flex-col">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Open/Closed</h3>
        <div className="mt-2 text-3xl font-bold text-indigo-600">
          {analytics.open_vs_closed_ratio}
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Active to closed ratio
        </p>
      </Card>
    </div>
  );
};
