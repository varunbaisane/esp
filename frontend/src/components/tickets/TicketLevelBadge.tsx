import type { TicketLevel } from "../../types/ticket";

interface TicketLevelBadgeProps {
  level: TicketLevel;
}

export const TicketLevelBadge = ({ level }: TicketLevelBadgeProps) => {
  const styles = {
    L1: "bg-blue-50 text-blue-700 border-blue-200",
    L2: "bg-indigo-50 text-indigo-700 border-indigo-200",
    L3: "bg-purple-50 text-purple-700 border-purple-200",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${styles[level]}`}
    >
      {level}
    </span>
  );
};
