import type { TicketPriority } from "../../types/ticket";
import { COLORS } from "../../styles/design-tokens";

interface TicketFormFieldsProps {
  title: string;
  setTitle: (value: string) => void;
  description: string;
  setDescription: (value: string) => void;
  priority: TicketPriority | "";
  setPriority: (value: TicketPriority | "") => void;
  disabled: boolean;
}

export const TicketFormFields = ({
  title,
  setTitle,
  description,
  setDescription,
  priority,
  setPriority,
  disabled
}: TicketFormFieldsProps) => {
  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          required
          disabled={disabled}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`w-full px-3 py-2 border border-gray-200 rounded-sm focus:outline-none ${COLORS.primary.ring["500"]} focus:border-cyan-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-400`}
          placeholder="Brief summary of the issue"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          rows={4}
          disabled={disabled}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className={`w-full px-3 py-2 border border-gray-200 rounded-sm focus:outline-none ${COLORS.primary.ring["500"]} focus:border-cyan-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-400`}
          placeholder="Detailed explanation of the problem..."
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
          Priority <span className="text-red-500">*</span>
        </label>
        <select
          id="priority"
          name="priority"
          required
          disabled={disabled}
          value={priority}
          onChange={(e) => setPriority(e.target.value as TicketPriority | "")}
          className={`w-full px-3 py-2 border border-gray-200 rounded-sm focus:outline-none ${COLORS.primary.ring["500"]} focus:border-cyan-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-400 bg-white`}
        >
          <option value="" disabled>Select Priority</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>
      </div>
    </div>
  );
};
