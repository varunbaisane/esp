import React, { useEffect, useState } from "react";
import type { User } from "../../types/user";
import { userService } from "../../services/userService";

import type { TicketLevel } from "../../types/ticket";
import { getUserHighestRank } from "../../utils/permissions";
import { ButtonLoader } from "./ButtonLoader";
import { Button } from "./Button";

interface AssignTicketModalProps {
  isOpen: boolean;
  ticketLevel: TicketLevel;
  onClose: () => void;
  onAssign: (assigneeId: number) => Promise<void>;
}

export const AssignTicketModal: React.FC<AssignTicketModalProps> = ({
  isOpen,
  ticketLevel,
  onClose,
  onAssign,
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | "">("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      const fetchUsers = async () => {
        setIsFetching(true);
        try {
          const data = await userService.getUsers();
          setUsers(data);
        } catch (err) {
          console.error("Failed to fetch users", err);
          setError("Could not load users.");
        } finally {
          setIsFetching(false);
        }
      };
      fetchUsers();
    } else {
      setSelectedUserId("");
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAssign = async () => {
    if (!selectedUserId) return;
    setIsLoading(true);
    setError(null);
    try {
      await onAssign(Number(selectedUserId));
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to assign ticket.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="px-6 py-5 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-900">Assign Ticket</h3>
        </div>
        
        <div className="px-6 py-5">
          {error && (
            <div className="mb-4 p-3 rounded bg-red-50 text-red-600 text-sm">
              {error}
            </div>
          )}

          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Select Engineer
          </label>
          
          {isFetching ? (
            <div className="text-sm text-gray-500 py-2">Loading engineers...</div>
          ) : (
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value ? Number(e.target.value) : "")}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2 px-3 border"
            >
              <option value="" disabled>-- Select an engineer --</option>
              {users
                .filter((user) => {
                  const rank = getUserHighestRank(user);
                  if (ticketLevel === "L1" && rank < 1) return false;
                  if (ticketLevel === "L2" && rank < 2) return false;
                  if (ticketLevel === "L3" && rank < 3) return false;
                  return true;
                })
                .map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.full_name} ({user.email})
                  </option>
              ))}
            </select>
          )}
        </div>
        
        <div className="px-6 py-4 bg-gray-50 flex justify-end gap-3 rounded-b-xl border-t border-gray-100">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="primary"
            onClick={handleAssign}
            disabled={!selectedUserId || isLoading}
          >
            {isLoading ? <ButtonLoader text="Assigning..." /> : "Assign"}
          </Button>
        </div>
      </div>
    </div>
  );
};
