import { useState } from "react";
import type { TicketCreate } from "../../types/ticket";
import type { User } from "../../types/user";
import { TicketFormFields } from "./TicketFormFields";
import { TicketFormActions } from "./TicketFormActions";
import { Card } from "../common/Card";

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
    <Card noPadding>
      <form onSubmit={handleSubmit} className="p-8">
        <div className="mb-6 border-b border-gray-100 pb-2">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Ticket Information</h3>
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
    </Card>
  );
};
