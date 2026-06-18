import { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import type { TicketSummary } from "../types/ticket";
import { TicketTable } from "../components/tickets/TicketTable";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";

export const TicketsPage = () => {
  const [tickets, setTickets] = useState<TicketSummary[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="space-y-6">
      <div className="pb-1 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tickets</h2>
        </div>
      </div>

      {loading && <LoadingState message="Loading tickets..." />}
      {error && <ErrorState message={error} />}
      {!loading && !error && tickets && <TicketTable tickets={tickets} />}
    </div>
  );
};
