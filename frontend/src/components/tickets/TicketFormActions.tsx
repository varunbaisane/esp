import { Link } from "react-router-dom";
import { COLORS } from "../../styles/design-tokens";

interface TicketFormActionsProps {
  loading: boolean;
}

export const TicketFormActions = ({ loading }: TicketFormActionsProps) => {
  return (
    <div className="pt-4 flex items-center justify-end space-x-4 border-t border-gray-200 mt-6">
      <Link 
        to="/tickets" 
        className="text-sm font-medium text-gray-500 hover:text-gray-900 px-4 py-2"
        aria-disabled={loading}
      >
        Cancel
      </Link>
      <button
        type="submit"
        disabled={loading}
        className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${COLORS.primary["600"]} ${COLORS.primary.hover.bg["700"]} focus:outline-none ${COLORS.primary.ring["500"]} focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors`}
      >
        {loading ? "Creating..." : "Create Ticket"}
      </button>
    </div>
  );
};
