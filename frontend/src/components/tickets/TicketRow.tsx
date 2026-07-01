import React from "react";
import { useNavigate } from "react-router-dom";
import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketPriorityBadge } from "./TicketPriorityBadge";
import { TicketLevelBadge } from "./TicketLevelBadge";
import { TicketSLABadge } from "./TicketSLABadge";
import { UserAvatar } from "../common/UserAvatar";
import { formatRelativeDateTime } from "../../lib/dateTime";

interface TicketRowProps {
  ticket: TicketSummary;
}

export const TicketRow = React.memo(({ ticket }: TicketRowProps) => {
  const navigate = useNavigate();

  const createdDate = formatRelativeDateTime(ticket.created_at);

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
        {ticket.assigned_to_name ? (
          <div className="flex items-center gap-2 text-gray-900">
            <UserAvatar name={ticket.assigned_to_name} size="sm" />
            <span>{ticket.assigned_to_name}</span>
          </div>
        ) : (
          <span className="text-gray-400 italic">Unassigned</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {createdDate}
      </td>
    </tr>
  );
}, (prevProps, nextProps) => {
  return prevProps.ticket.id === nextProps.ticket.id && 
         prevProps.ticket.status === nextProps.ticket.status &&
         prevProps.ticket.assigned_to_id === nextProps.ticket.assigned_to_id &&
         prevProps.ticket.sla_status === nextProps.ticket.sla_status;
});
