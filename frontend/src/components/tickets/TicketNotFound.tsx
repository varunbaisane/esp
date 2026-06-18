import { Link } from "react-router-dom";

export const TicketNotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="text-5xl mb-4">🔍</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">Ticket Not Found</h3>
      <p className="text-gray-500 text-center max-w-md mb-6">
        We couldn't find the ticket you're looking for. It may have been deleted, or the ID might be incorrect.
      </p>
      <Link 
        to="/tickets"
        className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
      >
        ← Back to Tickets
      </Link>
    </div>
  );
};
