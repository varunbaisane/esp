import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { ticketService } from "../services/ticketService";
import type { TicketRead } from "../types/ticket";
import { TicketDetail } from "../components/tickets/TicketDetail";
import { TicketNotFound } from "../components/tickets/TicketNotFound";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { PageContainer } from "../components/layout/PageContainer";

export const TicketDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<TicketRead | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState<boolean>(false);

  useEffect(() => {
    const fetchTicket = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      setNotFound(false);
      
      try {
        const data = await ticketService.getTicket(parseInt(id, 10));
        setTicket(data);
      } catch (err: unknown) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setNotFound(true);
        } else {
          setError(err instanceof Error ? err.message : "Unable to connect to backend while fetching ticket details.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTicket();
  }, [id]);

  return (
    <PageContainer className="max-w-4xl">
      <div>
        <div className="mb-4">
          <Link 
            to="/tickets" 
            className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors inline-flex items-center"
          >
            &larr; Back to Tickets
          </Link>
        </div>
        
        {loading && <LoadingState message="Loading ticket details..." />}
        {error && !notFound && <ErrorState message={error} />}
        {notFound && !loading && <TicketNotFound />}
        {!loading && !error && !notFound && ticket && <TicketDetail ticket={ticket} />}
      </div>
    </PageContainer>
  );
};
