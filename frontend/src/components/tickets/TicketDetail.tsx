import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketMetadata } from "./TicketMetadata";

interface TicketDetailProps {
  ticket: TicketSummary;
}

export const TicketDetail = ({ ticket }: TicketDetailProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div className="mb-6 border-b border-gray-100 pb-8">
        <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          Ticket #{ticket.id}
        </span>
        <h2 className="mt-2 text-3xl font-bold text-gray-900">
          {ticket.title}
        </h2>
        <div className="mt-4">
          <TicketStatusBadge status={ticket.status} />
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-sm font-medium text-gray-500 mb-3 uppercase tracking-wider">
          Description
        </h3>
        {ticket.description ? (
          <p className="text-base text-gray-900 whitespace-pre-wrap break-words leading-relaxed">
            {ticket.description}
          </p>
        ) : (
          <p className="text-base text-gray-900 italic">
            No description provided.
          </p>
        )}
      </div>

      <div className="pt-2 border-t border-gray-100">
        <TicketMetadata ticket={ticket} />
      </div>
    </div>
  );
};
