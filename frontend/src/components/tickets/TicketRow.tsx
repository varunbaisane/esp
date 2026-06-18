import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";

interface TicketRowProps {
  ticket: TicketSummary;
}

export const TicketRow = ({ ticket }: TicketRowProps) => {
  // Determine assignee display text based on user requirements
  const assigneeText = ticket.assigned_to_id !== null ? `User #${ticket.assigned_to_id}` : "Unassigned";

  // Format date
  const createdDate = new Date(ticket.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        #{ticket.id}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {ticket.title}
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
