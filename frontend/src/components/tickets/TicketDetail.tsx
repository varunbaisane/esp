import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketMetadata } from "./TicketMetadata";

interface TicketDetailProps {
  ticket: TicketSummary;
}

export const TicketDetail = ({ ticket }: TicketDetailProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div className="mb-6">
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

      <TicketMetadata ticket={ticket} />
    </div>
  );
};
