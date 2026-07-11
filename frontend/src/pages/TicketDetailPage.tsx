import { useEffect, useState, useContext, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useTicketSync } from "../context/TicketSyncContext";
import axios from "axios";
import { ticketService } from "../services/ticketService";
import type { TicketRead } from "../types/ticket";
import { TicketDetail } from "../components/tickets/TicketDetail";
import { AuditTimeline } from "../components/tickets/AuditTimeline";
import { TicketNotFound } from "../components/tickets/TicketNotFound";
import { StateMessage } from "../components/common/StateMessage";
import { CardSkeleton } from "../components/common/CardSkeleton";
import { TimelineSkeleton } from "../components/common/TimelineSkeleton";
import { PageContainer } from "../components/layout/PageContainer";
import { AuthContext } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const TicketDetailPage = () => {
  const authContext = useContext(AuthContext);
  const currentUser = authContext?.currentUser || null;
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<TicketRead | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState<boolean>(false);

  const { registerTicketRefresh, unregisterTicketRefresh } = useTicketSync();
  useDocumentTitle(ticket ? `Ticket #${ticket.id}` : id ? `Ticket #${id}` : "Ticket");

  const fetchTicketSilently = useCallback(async () => {
    if (!id) return;
    try {
      const data = await ticketService.getTicket(parseInt(id, 10));
      setTicket(data);
    } catch (err) {
      // Ignore background sync errors
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      const ticketId = parseInt(id, 10);
      registerTicketRefresh(ticketId, 'detail-page', fetchTicketSilently);
      return () => unregisterTicketRefresh(ticketId, 'detail-page');
    }
  }, [id, registerTicketRefresh, unregisterTicketRefresh, fetchTicketSilently]);

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
        
        {loading && (
          <div className="space-y-6">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <div className="mt-8">
              <TimelineSkeleton />
            </div>
          </div>
        )}
        {error && !notFound && (
          <StateMessage 
            title="Unable to load ticket details" 
            message={error} 
            type="error" 
            onRetry={() => window.location.reload()}
          />
        )}
        {notFound && !loading && <TicketNotFound />}
        {!loading && !error && !notFound && ticket && (
          <TicketDetail 
            ticket={ticket} 
            currentUser={currentUser}
            onUpdate={async (updateData) => {
              try {
                const updatedTicket = await ticketService.updateTicket(ticket.id, updateData);
                setTicket(updatedTicket);
                setError(null);
              } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                  setError(err.response?.data?.detail || "Failed to update ticket.");
                } else {
                  setError("Failed to update ticket.");
                }
              }
            }}
            onEscalate={async () => {
              try {
                const escalatedTicket = await ticketService.escalateTicket(ticket.id);
                setTicket(escalatedTicket);
                setError(null);
              } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                  setError(err.response?.data?.detail || "Failed to escalate ticket.");
                } else {
                  setError("Failed to escalate ticket.");
                }
              }
            }}
            onClaim={async () => {
              try {
                const claimedTicket = await ticketService.claimTicket(ticket.id);
                setTicket(claimedTicket);
                setError(null);
              } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                  setError(err.response?.data?.detail || "Failed to claim ticket.");
                } else {
                  setError("Failed to claim ticket.");
                }
                throw err;
              }
            }}
            onAssign={async (assigneeId: number) => {
              try {
                const assignedTicket = await ticketService.assignTicket(ticket.id, assigneeId);
                setTicket(assignedTicket);
                setError(null);
              } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                  setError(err.response?.data?.detail || "Failed to assign ticket.");
                } else {
                  setError("Failed to assign ticket.");
                }
                throw err;
              }
            }}
          />
        )}
        {!loading && !error && !notFound && ticket && (
          <div className="mt-8">
            <AuditTimeline key={ticket.updated_at} ticketId={ticket.id} />
          </div>
        )}
      </div>
    </PageContainer>
  );
};
