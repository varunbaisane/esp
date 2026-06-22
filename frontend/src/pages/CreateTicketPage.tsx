import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { ticketService } from "../services/ticketService";
import type { TicketCreate } from "../types/ticket";
import { TicketForm } from "../components/tickets/TicketForm";
import { FormError } from "../components/common/FormError";
import { PageContainer } from "../components/layout/PageContainer";

export const CreateTicketPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: TicketCreate) => {
    setLoading(true);
    setError(null);
    try {
      const newTicket = await ticketService.createTicket(data);
      navigate(`/tickets/${newTicket.id}`);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || err.message || "Unable to create ticket.");
      } else if (err instanceof Error) {
        setError(err.message || "Unable to create ticket.");
      } else {
        setError("Unable to create ticket.");
      }
      setLoading(false);
    }
  };

  return (
    <PageContainer className="max-w-3xl">
      <div>
        <div className="mb-4">
          <Link
            to="/tickets"
            className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors inline-flex items-center"
          >
            &larr; Back to Tickets
          </Link>
        </div>

        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Create Ticket</h2>
          <p className="mt-2 text-sm text-gray-500">Submit a new engineering support request.</p>
        </div>
      </div>

      {error && <FormError message={error} />}

      <TicketForm
        onSubmit={handleSubmit}
        loading={loading}
      />
    </PageContainer>
  );
};
