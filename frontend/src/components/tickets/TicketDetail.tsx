import type { TicketRead, TicketUpdate, TicketStatus } from "../../types/ticket";
import type { CurrentUser } from "../../types/auth";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketPriorityBadge } from "./TicketPriorityBadge";
import { TicketLevelBadge } from "./TicketLevelBadge";
import { useState } from "react";
import { TicketMetadata } from "./TicketMetadata";
import { Card } from "../common/Card";
import { ConfirmationModal } from "../common/ConfirmationModal";
import { AssignTicketModal } from "../common/AssignTicketModal";
import { getValidNextStates } from "../../utils/ticketWorkflow";
import { canEscalateTicket, canAssignTicket, canClaimTicket } from "../../utils/permissions";

interface TicketDetailProps {
  ticket: TicketRead;
  currentUser: CurrentUser | null;
  onUpdate: (data: TicketUpdate) => Promise<void>;
  onEscalate: () => Promise<void>;
  onClaim: () => Promise<void>;
  onAssign: (assigneeId: number) => Promise<void>;
}

export const TicketDetail = ({ ticket, currentUser, onUpdate, onEscalate, onClaim, onAssign }: TicketDetailProps) => {
  const [isEscalationModalOpen, setIsEscalationModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const validNextStates = getValidNextStates(ticket.status);
  const canEscalate = canEscalateTicket(currentUser, ticket.support_level);
  const canAssign = canAssignTicket(currentUser, ticket.support_level);
  const canClaim = canClaimTicket(currentUser, ticket.support_level);
  const nextLevel = ticket.support_level === "L1" ? "L2" : "L3";

  const handleEscalateConfirm = async () => {
    setIsEscalationModalOpen(false);
    await onEscalate();
  };

  return (
    <div className="space-y-6">
      {canEscalate && (
        <ConfirmationModal
          isOpen={isEscalationModalOpen}
          title="Escalate Ticket"
          description={
            <div className="flex flex-col gap-4 mt-2">
              <div className="text-gray-900 font-medium text-base">
                {ticket.title}
              </div>
              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg border border-gray-100">
                <div>
                  <span className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Current Level</span>
                  <span className="text-gray-900 font-semibold">{ticket.support_level}</span>
                </div>
                <div>
                  <span className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Next Level</span>
                  <span className="text-amber-600 font-bold">{nextLevel}</span>
                </div>
              </div>
              <p className="text-gray-600 mt-1">
                This action transfers ownership to the next support tier.
              </p>
            </div>
          }
          confirmText={`Escalate to ${nextLevel}`}
          onConfirm={handleEscalateConfirm}
          onCancel={() => setIsEscalationModalOpen(false)}
        />
      )}
      <AssignTicketModal
        isOpen={isAssignModalOpen}
        ticketLevel={ticket.support_level}
        onClose={() => setIsAssignModalOpen(false)}
        onAssign={onAssign}
      />
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
              <TicketLevelBadge level={ticket.support_level} />
              <TicketStatusBadge status={ticket.status} />
              <TicketPriorityBadge priority={ticket.priority} />
            </div>
            
            <div className="flex items-center gap-3 mt-4 text-sm bg-gray-50 p-2.5 rounded-lg border border-gray-100 max-w-fit">
              <span className="font-semibold text-gray-500 uppercase tracking-wide text-xs">Assigned To:</span>
              {ticket.assigned_to_name ? (
                <span className="font-bold text-gray-900">{ticket.assigned_to_name}</span>
              ) : (
                <span className="font-bold text-gray-400 italic">Unassigned</span>
              )}
              
              {!ticket.assigned_to_name && canClaim && (
                <button
                  onClick={onClaim}
                  className="ml-2 px-3 py-1 text-xs font-bold rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors border border-indigo-200 shadow-sm"
                >
                  Claim Ticket
                </button>
              )}
              
              {canAssign && (
                <button
                  onClick={() => setIsAssignModalOpen(true)}
                  className="ml-2 px-3 py-1 text-xs font-bold rounded bg-white text-gray-700 hover:bg-gray-100 transition-colors border border-gray-300 shadow-sm"
                >
                  Assign Ticket
                </button>
              )}
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
              {canEscalate && (
                <button
                  onClick={() => setIsEscalationModalOpen(true)}
                  className="px-4 py-2 text-sm font-semibold rounded-md border transition-all bg-amber-600 hover:bg-amber-700 text-white shadow-sm border-transparent"
                >
                  Escalate ↑
                </button>
              )}
            </div>
          )}
          {validNextStates.length === 0 && canEscalate && (
            <div className="flex flex-wrap gap-2 shrink-0">
              <button
                onClick={() => setIsEscalationModalOpen(true)}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all bg-amber-600 hover:bg-amber-700 text-white shadow-sm border-transparent"
              >
                Escalate ↑
              </button>
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
