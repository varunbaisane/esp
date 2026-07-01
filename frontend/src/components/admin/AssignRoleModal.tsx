import React, { useState } from 'react';
import type { UserSummaryResponse, RoleOperationRequest } from '../../types/user';
import { RoleOperation } from '../../types/user';
import { Button } from '../common/Button';
import { ButtonLoader } from '../common/ButtonLoader';

interface Props {
  user: UserSummaryResponse;
  isOpen: boolean;
  onClose: () => void;
  onAssign: (data: RoleOperationRequest) => Promise<void>;
}

export const AssignRoleModal: React.FC<Props> = ({ user, isOpen, onClose, onAssign }) => {
  const [selectedRoleCode, setSelectedRoleCode] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleClose = () => {
    if (isSubmitting) return;
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoleCode) return;
    
    setIsSubmitting(true);
    try {
      await onAssign({
        operation: RoleOperation.ASSIGN,
        role_code: selectedRoleCode
      });
      // Do not call onClose here because optimistic update will unmount the modal by clearing selection in UsersPage
    } catch {
      setIsSubmitting(false);
    }
  };

  const getRoleDisplayName = (code: string) => {
    return code.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={handleClose} />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900">
            {user.current_role ? 'Change Role' : 'Assign Role'}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Provisioning access for <span className="font-medium text-gray-900">{user.name}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="p-6">
            {user.current_role && (
              <div className="mb-4 p-3 bg-blue-50 text-blue-800 rounded-lg text-sm">
                <span className="font-semibold">Current Role:</span> {user.current_role.display_name}
              </div>
            )}

            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">
                Select New Role
              </label>
              <div className="space-y-2">
                {user.assignable_roles.length === 0 ? (
                  <div className="text-sm text-gray-500">You do not have permission to assign roles to this user.</div>
                ) : (
                  user.assignable_roles.map((roleCode) => (
                    <label key={roleCode} className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                      <input
                        type="radio"
                        name="role"
                        value={roleCode}
                        checked={selectedRoleCode === roleCode}
                        onChange={(e) => setSelectedRoleCode(e.target.value)}
                        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2"
                        disabled={isSubmitting}
                      />
                      <span className="ml-3 text-sm font-medium text-gray-900">
                        {getRoleDisplayName(roleCode)}
                      </span>
                    </label>
                  ))
                )}
              </div>
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
              variant="primary"
              disabled={isSubmitting || !selectedRoleCode}
            >
              {isSubmitting ? (
                <ButtonLoader text={user.current_role ? 'Updating...' : 'Assigning...'} />
              ) : (
                user.current_role ? 'Confirm Change' : 'Assign Role'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
