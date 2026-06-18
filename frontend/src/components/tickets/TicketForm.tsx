import { useState } from "react";
import type { TicketCreate } from "../../types/ticket";
import type { User } from "../../types/user";
import { TicketFormFields } from "./TicketFormFields";
import { TicketFormActions } from "./TicketFormActions";

interface TicketFormProps {
  users: User[];
  onSubmit: (data: TicketCreate) => void;
  loading: boolean;
}

export const TicketForm = ({ users, onSubmit, loading }: TicketFormProps) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [createdById, setCreatedById] = useState<number | "">("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || createdById === "") return;

    onSubmit({
      title,
      description,
      created_by_id: createdById,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h3 className="text-lg font-medium leading-6 text-gray-900">Ticket Details</h3>
        <p className="mt-1 text-sm text-gray-500">Provide the necessary information to file a new ticket.</p>
      </div>

      <TicketFormFields 
        users={users}
        title={title}
        setTitle={setTitle}
        description={description}
        setDescription={setDescription}
        createdById={createdById}
        setCreatedById={setCreatedById}
        disabled={loading}
      />
      
      <TicketFormActions loading={loading} />
    </form>
  );
};
