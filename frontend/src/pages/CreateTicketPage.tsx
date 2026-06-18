import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ticketService } from "../services/ticketService";
import { userService } from "../services/userService";
import type { TicketCreate } from "../types/ticket";
import type { User } from "../types/user";
import { TicketForm } from "../components/tickets/TicketForm";
import { FormError } from "../components/common/FormError";
import { LoadingState } from "../components/common/LoadingState";

export const CreateTicketPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [fetchingUsers, setFetchingUsers] = useState<boolean>(true);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await userService.getUsers();
        setUsers(data);
      } catch (err: any) {
        setError("Failed to load users for the dropdown.");
      } finally {
        setFetchingUsers(false);
      }
    };
    loadUsers();
  }, []);

  const handleSubmit = async (data: TicketCreate) => {
    setLoading(true);
    setError(null);
    try {
      const newTicket = await ticketService.createTicket(data);
      navigate(`/tickets/${newTicket.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Unable to create ticket.");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="pb-2">
        <Link 
          to="/tickets" 
          className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors inline-flex items-center"
        >
          &larr; Back to Tickets
        </Link>
      </div>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Create Ticket</h2>
      </div>

      {error && <FormError message={error} />}

      {fetchingUsers ? (
        <LoadingState message="Loading form requirements..." />
      ) : (
        <TicketForm 
          users={users} 
          onSubmit={handleSubmit} 
          loading={loading} 
        />
      )}
    </div>
  );
};
