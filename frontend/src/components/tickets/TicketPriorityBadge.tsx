import type { TicketPriority } from "../../types/ticket";

export const getPriorityBadgeStyle = (priority: TicketPriority) => {
  switch (priority) {
    case "CRITICAL":
      return "bg-red-50 text-red-700 border-red-200";
    case "HIGH":
      return "bg-orange-50 text-orange-700 border-orange-200";
    case "MEDIUM":
      return "bg-yellow-50 text-yellow-700 border-yellow-200";
    case "LOW":
      return "bg-gray-50 text-gray-700 border-gray-200";
    default:
      return "bg-gray-50 text-gray-700 border-gray-200";
  }
};

export const getPriorityTextColor = (priority: TicketPriority) => {
  switch (priority) {
    case "CRITICAL":
      return "text-red-700";
    case "HIGH":
      return "text-orange-700";
    case "MEDIUM":
      return "text-yellow-700";
    case "LOW":
      return "text-gray-700";
    default:
      return "text-gray-700";
  }
};

export const TicketPriorityBadge = ({ priority }: { priority: TicketPriority }) => {

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getPriorityBadgeStyle(priority)}`}>
      {priority}
    </span>
  );
};
