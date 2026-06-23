import type { SLAStatus } from "../../types/ticket";

interface TicketSLABadgeProps {
  status: SLAStatus;
}

export const TicketSLABadge = ({ status }: TicketSLABadgeProps) => {
  const getBadgeStyles = (status: SLAStatus) => {
    switch (status) {
      case "HEALTHY":
        return "bg-emerald-50 text-emerald-700 ring-emerald-600/20";
      case "AT_RISK":
        return "bg-amber-50 text-amber-700 ring-amber-600/20";
      case "BREACHED":
        return "bg-rose-50 text-rose-700 ring-rose-600/20";
      default:
        return "bg-gray-50 text-gray-700 ring-gray-600/20";
    }
  };

  const formatText = (status: SLAStatus) => {
    return status.replace("_", " ");
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold ring-1 ring-inset ${getBadgeStyles(status)}`}>
      {formatText(status)}
    </span>
  );
};
