import type { TicketRead, TicketUpdate, TicketStatus } from "../../types/ticket";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketPriorityBadge } from "./TicketPriorityBadge";
import { TicketMetadata } from "./TicketMetadata";
import { Card } from "../common/Card";
import { getValidNextStates } from "../../utils/ticketWorkflow";

interface TicketDetailProps {
  ticket: TicketRead;
  onUpdate: (data: TicketUpdate) => Promise<void>;
}

export const TicketDetail = ({ ticket, onUpdate }: TicketDetailProps) => {
  const validNextStates = getValidNextStates(ticket.status);
  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex flex-col gap-1">
            <h2 className="text-3xl font-black text-gray-900 tracking-tight">
              {ticket.title}
            </h2>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-sm font-semibold text-gray-400">
                Ticket #{ticket.id}
              </span>
              <TicketStatusBadge status={ticket.status} />
              <TicketPriorityBadge priority={ticket.priority} />
            </div>
          </div>

          {validNextStates.length > 0 && (
            <div className="flex flex-wrap gap-2 shrink-0">
              {validNextStates.map(state => {
                const isClosing = state === "CLOSED" || state === "RESOLVED";
                const buttonClass = isClosing
                  ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm border-transparent"
                  : "bg-cyan-600 hover:bg-cyan-700 text-white shadow-sm border-transparent";
                  
                return (
                  <button
                    key={state}
                    onClick={() => onUpdate({ status: state as TicketStatus })}
                    className={`px-4 py-2 text-sm font-semibold rounded-md border transition-all ${buttonClass}`}
                  >
                    Mark as {state.replace("_", " ")}
                  </button>
                );
              })}
            </div>
          )}
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
