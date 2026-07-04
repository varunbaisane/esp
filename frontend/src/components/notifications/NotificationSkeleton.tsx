import React from 'react';

export const NotificationSkeleton: React.FC = () => {
  return (
    <div className="animate-pulse space-y-4 p-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="flex gap-4 items-start">
          <div className="w-10 h-10 rounded-full bg-slate-200 flex-shrink-0" />
          <div className="flex-1 space-y-2 py-1">
            <div className="h-4 bg-slate-200 rounded w-3/4" />
            <div className="h-3 bg-slate-200 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
};
