import { Card } from "./Card";
import { Skeleton } from "./Skeleton";

export const CardSkeleton = () => {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-5 w-5 rounded-full" />
      </div>
      <Skeleton className="h-8 w-16 mb-2" />
      <Skeleton className="h-3 w-32" />
    </Card>
  );
};
