import type { TicketFilterStatus } from "../../types/ticket";
import { COLORS } from "../../styles/design-tokens";

interface TicketStatusFilterProps {
  value: TicketFilterStatus;
  onChange: (value: TicketFilterStatus) => void;
}

export const TicketStatusFilter = ({ value, onChange }: TicketStatusFilterProps) => {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TicketFilterStatus)}
        className={`block w-full pl-3 pr-10 py-2 border border-gray-300 text-base focus:outline-none ${COLORS.primary.ring["500"]} focus:ring-1 focus:border-cyan-500 sm:text-sm rounded-md shadow-sm bg-white cursor-pointer`}
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
