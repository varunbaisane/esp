import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Card = ({ children, className = "", noPadding = false }: CardProps) => {
  return (
    <div className={`rounded-sm border border-gray-200 bg-white ${noPadding ? "" : "p-6"} ${className}`}>
      {children}
    </div>
  );
};
