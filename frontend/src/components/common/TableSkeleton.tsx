import { Skeleton } from "./Skeleton";

interface TableSkeletonProps {
  rows?: number;
  cols?: number;
}

export const TableSkeleton = ({ rows = 5, cols = 5 }: TableSkeletonProps) => {
  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-3 flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={`h-${i}`} className="h-4 flex-1" />
        ))}
      </div>
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={`r-${rowIndex}`} className="px-6 py-4 flex gap-4 items-center">
            {Array.from({ length: cols }).map((_, colIndex) => (
              <Skeleton key={`c-${rowIndex}-${colIndex}`} className="h-4 flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};
