import { Card } from "./Card";
import { Skeleton } from "./Skeleton";

interface ChartSkeletonProps {
  type?: 'bar' | 'ring';
}

export const ChartSkeleton = ({ type = 'bar' }: ChartSkeletonProps) => {
  return (
    <Card className="p-6 w-full h-[384px] flex flex-col">
      <Skeleton className="h-4 w-40 mb-8" />
      
      {type === 'bar' ? (
        <div className="flex-1 flex items-end gap-2 px-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} style={{ height: `${Math.max(20, Math.random() * 100)}%` }} className="w-12">
              <Skeleton className="w-full h-full rounded-t-sm" />
            </div>
          ))}
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center gap-8">
          <div className="w-40 h-40 rounded-full border-[20px] border-gray-200 animate-pulse bg-transparent" />
          <div className="flex gap-4">
            <Skeleton className="w-16 h-3" />
            <Skeleton className="w-16 h-3" />
            <Skeleton className="w-16 h-3" />
          </div>
        </div>
      )}
    </Card>
  );
};
