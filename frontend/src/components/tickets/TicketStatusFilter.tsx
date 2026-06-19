import type { TicketFilterStatus } from "../../types/ticket";

interface TicketStatusFilterProps {
  value: TicketFilterStatus;
  onChange: (value: TicketFilterStatus) => void;
}

export const TicketStatusFilter = ({ value, onChange }: TicketStatusFilterProps) => {
  return (
    <div className="relative mb-6">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TicketFilterStatus)}
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm bg-white cursor-pointer"
      >
        <option value="ALL">All Statuses</option>
        <option value="OPEN">Open</option>
        <option value="IN_PROGRESS">In Progress</option>
        <option value="RESOLVED">Resolved</option>
        <option value="CLOSED">Closed</option>
      </select>
    </div>
  );
};
