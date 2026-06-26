import { Skeleton } from "./Skeleton";

export const TimelineSkeleton = () => {
  return (
    <div className="relative pl-8 space-y-8">
      {/* Vertical line connecting nodes */}
      <div className="absolute top-0 bottom-0 left-[11px] w-0.5 bg-gray-200"></div>
      
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="relative">
          {/* Circle node */}
          <div className="absolute -left-8 mt-1.5 h-6 w-6 rounded-full border-2 border-gray-200 bg-white"></div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
            <Skeleton className="h-4 w-1/3 mb-3" />
            <Skeleton className="h-3 w-1/4 mb-4" />
            <div className="bg-gray-50 p-3 rounded space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-5/6" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
