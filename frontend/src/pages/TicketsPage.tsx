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
import { PageContainer } from "../components/layout/PageContainer";
import { Card } from "../components/common/Card";
import { COLORS } from "../styles/design-tokens";

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
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Tickets</h2>
          <p className="mt-2 text-sm text-gray-500">Browse and manage all engineering support tickets.</p>
        </div>
        <Link
          to="/tickets/new"
          className={`inline-flex items-center gap-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${COLORS.primary["600"]} ${COLORS.primary.hover.bg["700"]} transition-colors shadow-sm whitespace-nowrap`}
        >
          <span className="text-xl mr-1 leading-none">+</span> <span className="font-semibold">Create Ticket</span>
        </Link>
      </div>

      {loading && <LoadingState message="Loading tickets..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && tickets && filteredTickets && (
        <Card noPadding>
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex flex-col sm:flex-row gap-4 justify-between items-center rounded-t-xl">
            <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto flex-1">
              <div className="sm:max-w-xs w-full">
                <TicketSearch value={searchQuery} onChange={setSearchQuery} />
              </div>
              <div className="sm:w-48 w-full">
                <TicketStatusFilter value={statusFilter} onChange={setStatusFilter} />
              </div>
            </div>
            <div className="text-sm font-medium text-gray-500 whitespace-nowrap">
              Showing {filteredTickets.length} of {tickets.length} tickets{statusFilter !== "ALL" && ` • Status: ${statusFilter}`}
            </div>
          </div>
          {filteredTickets.length > 0 ? (
            <TicketTable tickets={filteredTickets} />
          ) : (
            <div className="p-6">
              <EmptySearchResults />
            </div>
          )}
        </Card>
      )}
    </PageContainer>
  );
};
