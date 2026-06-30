import type { TicketRead, TicketUpdate, TicketStatus } from "../../types/ticket";
import type { CurrentUser } from "../../types/auth";
import { TicketStatusBadge } from "./TicketStatusBadge";
import { TicketPriorityBadge, getPriorityBadgeStyle } from "./TicketPriorityBadge";
import { TicketLevelBadge } from "./TicketLevelBadge";
import { UserAvatar } from "../common/UserAvatar";
import { useState, useMemo } from "react";
import { ButtonLoader } from "../common/ButtonLoader";
import { TicketMetadata } from "./TicketMetadata";
import { Card } from "../common/Card";
import { ConfirmationModal } from "../common/ConfirmationModal";
import { AssignTicketModal } from "../common/AssignTicketModal";
import { canEscalateTicket, canClaimTicket } from "../../utils/permissions";
import { getTicketPermissions } from "../../lib/ticketPermissions";

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
  const canEscalate = canEscalateTicket(currentUser, ticket.support_level);
  const canClaim = canClaimTicket(currentUser, ticket.support_level);
  const nextLevel = ticket.support_level === "L1" ? "L2" : "L3";
  const permissions = useMemo(() => getTicketPermissions(currentUser, ticket), [currentUser, ticket]);

  const [activeAction, setActiveAction] = useState<string | null>(null);

  const handleEscalateConfirm = async () => {
    setActiveAction("escalate");
    try {
      await onEscalate();
      setIsEscalationModalOpen(false);
    } finally {
      setActiveAction(null);
    }
  };

  const handleClaim = async () => {
    setActiveAction("claim");
    try { await onClaim(); } finally { setActiveAction(null); }
  };

  const handleUpdate = async (state: TicketStatus) => {
    setActiveAction(`update_${state}`);
    try { await onUpdate({ status: state }); } finally { setActiveAction(null); }
  };

  const handlePriorityChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newPriority = e.target.value as any;
    setActiveAction(`update_priority`);
    try { await onUpdate({ priority: newPriority }); } finally { setActiveAction(null); }
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
          isLoading={activeAction === "escalate"}
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
              
              {permissions.canEditPriority ? (
                <div className="flex items-center">
                  <select
                    value={ticket.priority}
                    onChange={handlePriorityChange}
                    disabled={activeAction === "update_priority"}
                    className={`text-xs font-semibold rounded-full border shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500 py-1 pl-3 pr-8 appearance-none disabled:opacity-50 transition-colors text-center ${getPriorityBadgeStyle(ticket.priority)}`}
                    style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundPosition: 'right 0.3rem center', backgroundRepeat: 'no-repeat', backgroundSize: '1.2em 1.2em' }}
                  >
                    <option value="LOW" className="bg-white text-gray-900 text-left">LOW</option>
                    <option value="MEDIUM" className="bg-white text-gray-900 text-left">MEDIUM</option>
                    <option value="HIGH" className="bg-white text-gray-900 text-left">HIGH</option>
                    <option value="CRITICAL" className="bg-white text-gray-900 text-left">CRITICAL</option>
                  </select>
                  {activeAction === "update_priority" && <span className="ml-2"><ButtonLoader size="sm" /></span>}
                </div>
              ) : (
                <TicketPriorityBadge priority={ticket.priority} />
              )}
            </div>
            
            <div className="flex items-center gap-3 mt-4 text-sm bg-gray-50 p-2.5 rounded-lg border border-gray-100 max-w-fit">
              <span className="font-semibold text-gray-500 uppercase tracking-wide text-xs">Assigned To:</span>
              {ticket.assigned_to_name ? (
                <div className="flex items-center gap-2">
                  <UserAvatar name={ticket.assigned_to_name} size="sm" />
                  <span className="font-bold text-gray-900">{ticket.assigned_to_name}</span>
                </div>
              ) : (
                <span className="font-bold text-gray-400 italic">Unassigned</span>
              )}
              
              {!ticket.assigned_to_name && canClaim && (
                <button
                  onClick={handleClaim}
                  disabled={activeAction === "claim"}
                  className="ml-2 px-3 py-1 text-xs font-bold rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors border border-indigo-200 shadow-sm disabled:opacity-50"
                >
                  {activeAction === "claim" ? <ButtonLoader text="Claiming..." size="sm" /> : "Claim Ticket"}
                </button>
              )}
              
              {(ticket.assigned_to_name ? permissions.canChangeAssignee : permissions.canAssign) && (
                <button
                  onClick={() => setIsAssignModalOpen(true)}
                  className="ml-2 px-3 py-1 text-xs font-bold rounded bg-white text-gray-700 hover:bg-gray-100 transition-colors border border-gray-300 shadow-sm"
                >
                  {ticket.assigned_to_name ? "Change Assignee" : "Assign Ticket"}
                </button>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-2 shrink-0 mt-4 sm:mt-0">
            {permissions.canStartProgress && (
              <button
                onClick={() => handleUpdate("IN_PROGRESS")}
                disabled={activeAction === "update_IN_PROGRESS"}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all disabled:opacity-50 bg-cyan-600 hover:bg-cyan-700 text-white shadow-sm border-transparent"
              >
                {activeAction === "update_IN_PROGRESS" ? <ButtonLoader text="Starting Progress..." /> : "Start Progress"}
              </button>
            )}
            {permissions.canResolve && (
              <button
                onClick={() => handleUpdate("RESOLVED")}
                disabled={activeAction === "update_RESOLVED"}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all disabled:opacity-50 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm border-transparent"
              >
                {activeAction === "update_RESOLVED" ? <ButtonLoader text="Resolving..." /> : "Resolve Ticket"}
              </button>
            )}
            {permissions.canClose && (
              <button
                onClick={() => handleUpdate("CLOSED")}
                disabled={activeAction === "update_CLOSED"}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all disabled:opacity-50 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm border-transparent"
              >
                {activeAction === "update_CLOSED" ? <ButtonLoader text="Closing..." /> : "Close Ticket"}
              </button>
            )}
            {permissions.canReopen && (
              <button
                onClick={() => handleUpdate("OPEN")}
                disabled={activeAction === "update_OPEN"}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all disabled:opacity-50 bg-cyan-600 hover:bg-cyan-700 text-white shadow-sm border-transparent"
              >
                {activeAction === "update_OPEN" ? <ButtonLoader text="Reopening..." /> : "Reopen Ticket"}
              </button>
            )}
            {canEscalate && (
              <button
                onClick={() => setIsEscalationModalOpen(true)}
                className="px-4 py-2 text-sm font-semibold rounded-md border transition-all bg-amber-600 hover:bg-amber-700 text-white shadow-sm border-transparent"
              >
                Escalate ↑
              </button>
            )}
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
