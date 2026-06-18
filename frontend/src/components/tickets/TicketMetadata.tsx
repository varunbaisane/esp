import type { TicketSummary } from "../../types/ticket";

interface TicketMetadataProps {
  ticket: TicketSummary;
}

export const TicketMetadata = ({ ticket }: TicketMetadataProps) => {
  const createdDate = new Date(ticket.created_at).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const updatedDate = new Date(ticket.updated_at).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const assigneeText = ticket.assigned_to_id !== null ? `User #${ticket.assigned_to_id}` : "Unassigned";

  return (
    <div className="mt-8 border-t border-gray-200 pt-6">
      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
        <div className="sm:col-span-1">
          <dt className="text-sm font-medium text-gray-500 uppercase tracking-wide">Created By</dt>
          <dd className="mt-1 text-base text-gray-900">User #{ticket.created_by_id}</dd>
        </div>
        <div className="sm:col-span-1">
          <dt className="text-sm font-medium text-gray-500 uppercase tracking-wide">Assigned To</dt>
          <dd className="mt-1 text-base text-gray-900">{assigneeText}</dd>
        </div>
        <div className="sm:col-span-1">
          <dt className="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</dt>
          <dd className="mt-1 text-base text-gray-900">{createdDate}</dd>
        </div>
        <div className="sm:col-span-1">
          <dt className="text-sm font-medium text-gray-500 uppercase tracking-wide">Updated</dt>
          <dd className="mt-1 text-base text-gray-900">{updatedDate}</dd>
        </div>
      </dl>
    </div>
  );
};
