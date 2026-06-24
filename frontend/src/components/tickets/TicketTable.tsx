import type { TicketSummary } from "../../types/ticket";
import { TicketRow } from "./TicketRow";
import { EmptyTickets } from "./EmptyTickets";

interface TicketTableProps {
  tickets: TicketSummary[];
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (column: string) => void;
}

export const TicketTable = ({ tickets, sortBy, sortOrder, onSort }: TicketTableProps) => {
  const SortIndicator = ({ column }: { column: string }) => {
    if (sortBy !== column) return <span className="ml-1 text-gray-300 opacity-0 group-hover:opacity-100">↑</span>;
    return <span className="ml-1 text-indigo-500">{sortOrder === "asc" ? "↑" : "↓"}</span>;
  };

  const getHeaderClass = (sortable: boolean) => {
    const base = "px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider";
    if (sortable && onSort) {
      return `${base} cursor-pointer group hover:bg-gray-100 transition-colors select-none`;
    }
    return base;
  };

  const handleSort = (column: string) => {
    if (onSort) onSort(column);
  };
  if (tickets.length === 0) {
    return <EmptyTickets />;
  }

  return (
    <div className="overflow-x-auto w-full">
      <table className="w-full text-left border-collapse whitespace-nowrap">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50/50">
            <th className={getHeaderClass(false)}>
              ID
            </th>
            <th className={getHeaderClass(false)}>
              Title
            </th>
            <th className={getHeaderClass(true)} onClick={() => handleSort("level")}>
              <div className="flex items-center">Level <SortIndicator column="level" /></div>
            </th>
            <th className={getHeaderClass(true)} onClick={() => handleSort("priority")}>
              <div className="flex items-center">Priority <SortIndicator column="priority" /></div>
            </th>
            <th className={getHeaderClass(true)} onClick={() => handleSort("sla_status")}>
              <div className="flex items-center">SLA <SortIndicator column="sla_status" /></div>
            </th>
            <th className={getHeaderClass(false)}>
              Status
            </th>
            <th className={getHeaderClass(false)}>
              Assignee
            </th>
            <th className={getHeaderClass(true)} onClick={() => handleSort("created_at")}>
              <div className="flex items-center">Created <SortIndicator column="created_at" /></div>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {tickets.map((ticket) => (
            <TicketRow key={ticket.id} ticket={ticket} />
          ))}
        </tbody>
      </table>
    </div>
  );
};
