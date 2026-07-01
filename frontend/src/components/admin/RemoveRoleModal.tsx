import React, { useState } from 'react';
import type { UserSummaryResponse, RoleOperationRequest } from '../../types/user';
import { RoleOperation } from '../../types/user';
import { Button } from '../common/Button';
import { ButtonLoader } from '../common/ButtonLoader';

interface Props {
  user: UserSummaryResponse;
  isOpen: boolean;
  onClose: () => void;
  onRemove: (data: RoleOperationRequest) => Promise<void>;
}

export const RemoveRoleModal: React.FC<Props> = ({ user, isOpen, onClose, onRemove }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !user.current_role) return null;

  const handleClose = () => {
    if (isSubmitting) return;
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onRemove({
        operation: RoleOperation.REMOVE,
        role_code: user.current_role!.code
      });
      // Do not call onClose here because optimistic update will unmount the modal by clearing selection in UsersPage
    } catch {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={handleClose} />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden border border-red-100 animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-gray-100 bg-red-50/50">
          <div className="flex items-center gap-3 text-red-600">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-semibold">Remove Role</h2>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="p-6">
            <p className="text-sm text-gray-700">
              Are you sure you want to remove the <span className="font-semibold text-gray-900">{user.current_role.display_name}</span> role from <span className="font-semibold text-gray-900">{user.name}</span>?
            </p>
            
            <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100">
              <p className="text-sm text-yellow-800">
                This action will transition the user back to <strong>Pending Approval</strong> state. They will immediately lose access to the platform.
              </p>
            </div>
          </div>

          <div className="px-6 py-4 bg-gray-50 flex justify-end gap-3 border-t border-gray-100 rounded-b-xl">
            <Button
              type="button"
              variant="secondary"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="danger"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <ButtonLoader text="Removing..." />
              ) : (
                'Confirm Removal'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
