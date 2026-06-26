import type { TicketSummary } from "../../types/ticket";
import { TicketTable } from "../tickets/TicketTable";
import { Card } from "../common/Card";
import { Link } from "react-router-dom";
import { TableSkeleton } from "../common/TableSkeleton";

interface MyQueueTableProps {
  tickets: TicketSummary[];
  total: number;
  isLoading?: boolean;
}

export const MyQueueTable = ({ tickets, total, isLoading }: MyQueueTableProps) => {
  return (
    <Card noPadding>
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-col sm:flex-row gap-2 justify-between items-center rounded-t-xl">
        <h3 className="font-bold text-gray-800">Top Priority Assigned Tickets</h3>
        {total > 0 && (
          <span className="text-sm font-medium text-gray-500">
            Showing {tickets.length} of {total} assigned tickets
          </span>
        )}
      </div>
      
      {isLoading ? (
        <TableSkeleton rows={3} />
      ) : tickets.length > 0 ? (
        <TicketTable tickets={tickets} />
      ) : (
        <div className="p-8 text-center text-gray-500">
          No active tickets assigned to you. You're all caught up!
        </div>
      )}
      
      <div className="p-4 border-t border-gray-200 bg-gray-50 text-center rounded-b-xl">
        <Link 
          to="/tickets?assigned_to=mine&status=ACTIVE"
          className="text-indigo-600 hover:text-indigo-800 font-semibold text-sm transition-colors"
        >
          View Full Queue &rarr;
        </Link>
      </div>
    </Card>
  );
};
