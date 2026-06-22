import { useState } from "react";
import type { TicketCreate, TicketPriority } from "../../types/ticket";
import { TicketFormFields } from "./TicketFormFields";
import { TicketFormActions } from "./TicketFormActions";
import { Card } from "../common/Card";

interface TicketFormProps {
  onSubmit: (data: TicketCreate) => void;
  loading: boolean;
}

export const TicketForm = ({ onSubmit, loading }: TicketFormProps) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TicketPriority | "">("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || priority === "") return;

    onSubmit({
      title,
      description,
      priority,
    });
  };

  return (
    <Card noPadding>
      <form onSubmit={handleSubmit} className="p-8">
        <div className="mb-6 border-b border-gray-100 pb-2">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Ticket Information</h3>
        </div>

        <TicketFormFields 
          title={title}
          setTitle={setTitle}
          description={description}
          setDescription={setDescription}
          priority={priority}
          setPriority={setPriority}
          disabled={loading}
        />
        
        <TicketFormActions loading={loading} />
      </form>
    </Card>
  );
};
