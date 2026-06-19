import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { ticketService } from "../services/ticketService";
import type { TicketSummary, TicketFilterStatus } from "../types/ticket";
import { TicketTable } from "../components/tickets/TicketTable";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { TicketSearch } from "../components/tickets/TicketSearch";
import { TicketStatusFilter } from "../components/tickets/TicketStatusFilter";
import { EmptySearchResults } from "../components/tickets/EmptySearchResults";

export const TicketsPage = () => {
  const [tickets, setTickets] = useState<TicketSummary[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<TicketFilterStatus>("ALL");

  useEffect(() => {
    const fetchTickets = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await ticketService.getTickets();
        setTickets(data);
      } catch (err: any) {
        setError(err.message || "Unable to connect to backend while fetching tickets.");
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  const filteredTickets = useMemo(() => {
    if (!tickets) return null;
    
    let result = tickets;

    if (statusFilter !== "ALL") {
      result = result.filter(ticket => ticket.status === statusFilter);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.trim().toLowerCase();
      result = result.filter(ticket =>
        ticket.id.toString().includes(query) ||
        ticket.title.toLowerCase().includes(query) ||
        ticket.status.toLowerCase().includes(query)
      );
    }
    
    return result;
  }, [tickets, searchQuery, statusFilter]);

  return (
    <div className="space-y-6">
      <div className="pb-1 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tickets</h2>
        </div>
        <Link
          to="/tickets/new"
          className="inline-flex items-center gap-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-sm"
        >
          <span className="text-xl mr-1 leading-none">+</span> <span className="font-semibold">Create Ticket</span>
        </Link>
      </div>

      {loading && <LoadingState message="Loading tickets..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && tickets && filteredTickets && (
        <>
          <div className="flex flex-col mb-4">
            <div className="flex flex-col sm:flex-row gap-4 mb-2">
              <div className="flex-1">
                <TicketSearch value={searchQuery} onChange={setSearchQuery} />
              </div>
              <div className="sm:w-64">
                <TicketStatusFilter value={statusFilter} onChange={setStatusFilter} />
              </div>
            </div>
            <div className="text-sm text-gray-500 text-right mt-1">
              Showing {filteredTickets.length} of {tickets.length} tickets{statusFilter !== "ALL" && ` • Status: ${statusFilter}`}
            </div>
          </div>
          {filteredTickets.length > 0 ? (
            <TicketTable tickets={filteredTickets} />
          ) : (
            <EmptySearchResults />
          )}
        </>
      )}
    </div>
  );
};
