import type { ReactNode } from "react";

interface PageContainerProps {
  children: ReactNode;
  className?: string;
}

export const PageContainer = ({ children, className = "" }: PageContainerProps) => {
  return (
    <div className={`max-w-7xl mx-auto space-y-8 ${className}`}>
      {children}
    </div>
  );
};
