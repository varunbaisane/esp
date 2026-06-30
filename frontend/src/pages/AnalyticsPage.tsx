import { useEffect, useState } from "react";
import { PageContainer } from "../components/layout/PageContainer";
import { analyticsService } from "../services/analyticsService";
import type { AnalyticsResponse } from "../types/analytics";
import { StateMessage } from "../components/common/StateMessage";
import { ChartSkeleton } from "../components/common/ChartSkeleton";
import { AnalyticsSummary } from "../components/analytics/AnalyticsSummary";
import { StatusDistributionChart } from "../components/analytics/StatusDistributionChart";
import { PriorityDistributionChart } from "../components/analytics/PriorityDistributionChart";
import { LevelDistributionChart } from "../components/analytics/LevelDistributionChart";
import { WorkloadDistributionChart } from "../components/analytics/WorkloadDistributionChart";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const AnalyticsPage = () => {
  useDocumentTitle("Analytics");
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await analyticsService.getAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.error("Failed to fetch analytics:", err);
        setError("Failed to load analytics data.");
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (error) {
    return (
      <PageContainer>
        <StateMessage 
          title="Unable to load analytics" 
          message={error} 
          type="error" 
          onRetry={() => window.location.reload()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">
          Operational metrics and health indicators
        </p>
      </div>

      <AnalyticsSummary analytics={analytics} isLoading={loading} />

      <h2 className="text-lg font-bold text-gray-900 mt-10 mb-4 border-b border-gray-200 pb-2">Ticket Distribution</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        {loading || !analytics ? (
          <>
            <ChartSkeleton type="ring" />
            <ChartSkeleton />
            <ChartSkeleton />
          </>
        ) : (
          <>
            <StatusDistributionChart data={analytics.distribution.by_status} />
            <PriorityDistributionChart data={analytics.distribution.by_priority} />
            <LevelDistributionChart data={analytics.distribution.by_level} />
          </>
        )}
      </div>

      <h2 className="text-lg font-bold text-gray-900 mt-10 mb-4 border-b border-gray-200 pb-2">Workload Distribution</h2>
      <div className="mb-10">
        {loading || !analytics ? (
          <ChartSkeleton />
        ) : (
          <WorkloadDistributionChart data={analytics.workload.workload_distribution} />
        )}
      </div>
    </PageContainer>
  );
};
