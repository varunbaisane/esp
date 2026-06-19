import type { TicketSummary } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketMetadata } from "./TicketMetadata";
import { Card } from "../common/Card";

interface TicketDetailProps {
  ticket: TicketSummary;
}

export const TicketDetail = ({ ticket }: TicketDetailProps) => {
  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-col gap-1">
          <h2 className="text-3xl font-black text-gray-900 tracking-tight">
            {ticket.title}
          </h2>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-sm font-semibold text-gray-400">
              Ticket #{ticket.id}
            </span>
            <TicketStatusBadge status={ticket.status} />
          </div>
        </div>
      </Card>

      <Card>
        <h3 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest border-b border-gray-100 pb-2">
          Description
        </h3>
        <div className="pt-2">
          {ticket.description ? (
            <p className="text-base text-gray-800 whitespace-pre-wrap break-words leading-relaxed">
              {ticket.description}
            </p>
          ) : (
            <p className="text-base text-gray-400 italic">
              No description provided.
            </p>
          )}
        </div>
      </Card>

      <Card>
        <h3 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest border-b border-gray-100 pb-2">
          Metadata
        </h3>
        <TicketMetadata ticket={ticket} />
      </Card>
    </div>
  );
};
