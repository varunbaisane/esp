import { useNavigate } from "react-router-dom";
import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketPriorityBadge } from "./TicketPriorityBadge";
import { TicketLevelBadge } from "./TicketLevelBadge";
import { TicketSLABadge } from "./TicketSLABadge";

interface TicketRowProps {
  ticket: TicketSummary;
}

export const TicketRow = ({ ticket }: TicketRowProps) => {
  const navigate = useNavigate();

  // Determine assignee display text based on user requirements
  const assigneeText = ticket.assigned_to_name || "Unassigned";

  // Format date
  const createdDate = new Date(ticket.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  return (
    <tr
      onClick={() => navigate(`/tickets/${ticket.id}`)}
      className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
    >
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        #{ticket.id}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {ticket.title}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <TicketLevelBadge level={ticket.support_level} />
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <TicketPriorityBadge priority={ticket.priority} />
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <TicketSLABadge status={ticket.sla_status} />
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <TicketStatusBadge status={ticket.status} />
      </td>

      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <span className={ticket.assigned_to_id ? "text-gray-900" : "text-gray-400 italic"}>
          {assigneeText}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {createdDate}
      </td>
    </tr>
  );
};
