import type { User } from "../../types/user";

interface TicketFormFieldsProps {
  users: User[];
  title: string;
  setTitle: (value: string) => void;
  description: string;
  setDescription: (value: string) => void;
  createdById: number | "";
  setCreatedById: (value: number | "") => void;
  disabled: boolean;
}

export const TicketFormFields = ({
  users,
  title,
  setTitle,
  description,
  setDescription,
  createdById,
  setCreatedById,
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
          placeholder="Detailed explanation of the problem..."
        />
      </div>

      <div>
        <label htmlFor="createdById" className="block text-sm font-medium text-gray-700 mb-1">
          Created By <span className="text-red-500">*</span>
        </label>
        <select
          id="createdById"
          name="createdById"
          required
          disabled={disabled || users.length === 0}
          value={createdById}
          onChange={(e) => setCreatedById(e.target.value ? Number(e.target.value) : "")}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500 bg-white"
        >
          <option value="" disabled>Select User</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.username} (User #{user.id})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};
