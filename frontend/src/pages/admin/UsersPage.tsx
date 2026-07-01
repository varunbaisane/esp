import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { userService } from '../../services/userService';
import type { UserSummaryResponse, RoleOperationRequest } from '../../types/user';
import { AssignRoleModal } from '../../components/admin/AssignRoleModal';
import { RemoveRoleModal } from '../../components/admin/RemoveRoleModal';
import { TableSkeleton } from '../../components/common/TableSkeleton';
import { useNotification } from '../../hooks/useNotification';
import { PageContainer } from '../../components/layout/PageContainer';
import { Card } from '../../components/common/Card';

export const UsersPage: React.FC = () => {
  const { currentUser } = useAuth();
  const notify = useNotification();
  
  const [users, setUsers] = useState<UserSummaryResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefetching, setIsRefetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [roleFilter, setRoleFilter] = useState('All');

  const [selectedUserForAssign, setSelectedUserForAssign] = useState<UserSummaryResponse | null>(null);
  const [selectedUserForRemove, setSelectedUserForRemove] = useState<UserSummaryResponse | null>(null);

  const fetchUsers = useCallback(async (background = false) => {
    try {
      if (background) {
        setIsRefetching(true);
      } else {
        setIsLoading(true);
      }
      setError(null);
      
      const data = await userService.getUsers({
        search: search || undefined,
        status: statusFilter !== 'All' ? statusFilter : undefined,
        role: roleFilter !== 'All' ? roleFilter : undefined,
      });
      setUsers(data);
    } catch (err) {
      setError('Failed to fetch users.');
      console.error(err);
    } finally {
      setIsLoading(false);
      setIsRefetching(false);
    }
  }, [search, statusFilter, roleFilter]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchUsers();
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [fetchUsers]);

  const handleAssignRole = async (data: RoleOperationRequest) => {
    if (!selectedUserForAssign) return;
    try {
      await userService.operateUserRole(selectedUserForAssign.id, data);
      notify.success("Role updated successfully.");
      
      // Optimistic update
      setUsers(prev => prev.map(u => 
        u.id === selectedUserForAssign.id 
          ? { ...u, current_role: { code: data.role_code, display_name: data.role_code.replace('_', ' ') }, account_status: 'ACTIVE' } 
          : u
      ));
      
      setSelectedUserForAssign(null);
      fetchUsers(true); // Background refetch
    } catch (err: any) {
      notify.error(err.response?.data?.detail || 'You do not have permission to perform this action.');
      throw err;
    }
  };

  const handleRemoveRole = async (data: RoleOperationRequest) => {
    if (!selectedUserForRemove) return;
    try {
      await userService.operateUserRole(selectedUserForRemove.id, data);
      notify.success("Role removed successfully.");
      
      // Optimistic update
      setUsers(prev => prev.map(u => 
        u.id === selectedUserForRemove.id 
          ? { ...u, current_role: null, account_status: 'PENDING_APPROVAL' } 
          : u
      ));
      
      setSelectedUserForRemove(null);
      fetchUsers(true); // Background refetch
    } catch (err: any) {
      notify.error(err.response?.data?.detail || 'You do not have permission to perform this action.');
      throw err;
    }
  };

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Active</span>;
      case 'PENDING_APPROVAL':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Pending</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">User Administration</h2>
            <p className="mt-2 text-sm text-gray-500">
              Manage engineering roles and organizational access.
            </p>
          </div>
          {isRefetching && (
            <div className="flex items-center gap-2 text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full">
              <svg className="animate-spin h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Refreshing...</span>
            </div>
          )}
        </div>
      </div>

      <Card noPadding>
        {error && (
          <div className="m-4 p-4 rounded-md bg-red-50 text-red-700 text-sm border border-red-200">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-200 mb-6 mx-4 mt-4">
          <div className="flex flex-wrap items-end gap-4 sm:gap-6">
            <div className="flex flex-col gap-1.5 w-full sm:w-auto flex-1 min-w-[200px]">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Search Users</label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search by name or email..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  disabled={isLoading && users.length === 0}
                  className="w-full bg-gray-50/50 border border-gray-200 text-gray-700 py-2.5 px-4 rounded-xl leading-tight focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium text-sm shadow-sm hover:border-gray-300 placeholder:text-gray-400 disabled:opacity-50"
                />
              </div>
            </div>
            
            <div className="flex flex-col gap-1.5 w-full sm:w-auto flex-1 min-w-[160px]">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Role</label>
              <div className="relative">
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  disabled={isLoading && users.length === 0}
                  className="w-full appearance-none bg-gray-50/50 border border-gray-200 text-gray-700 py-2.5 px-4 pr-8 rounded-xl leading-tight focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium text-sm shadow-sm hover:border-gray-300 disabled:opacity-50"
                >
                  <option value="All" className="font-medium">All Roles</option>
                  <option value="Pending" className="font-medium">Pending Role</option>
                  <option value="SUPPORT_L1" className="font-medium">Support L1</option>
                  <option value="SUPPORT_L2" className="font-medium">Support L2</option>
                  <option value="SUPPORT_L3" className="font-medium">Support L3</option>
                  <option value="ENGINEERING_MANAGER" className="font-medium">Engineering Manager</option>
                  <option value="ADMIN" className="font-medium">Administrator</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-400">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                  </svg>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5 w-full sm:w-auto flex-1 min-w-[160px]">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Status</label>
              <div className="relative">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  disabled={isLoading && users.length === 0}
                  className="w-full appearance-none bg-gray-50/50 border border-gray-200 text-gray-700 py-2.5 px-4 pr-8 rounded-xl leading-tight focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium text-sm shadow-sm hover:border-gray-300 disabled:opacity-50"
                >
                  <option value="All" className="font-medium">All Statuses</option>
                  <option value="ACTIVE" className="font-medium">Active</option>
                  <option value="PENDING_APPROVAL" className="font-medium">Pending Approval</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-400">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                  </svg>
                </div>
              </div>
            </div>
            
            {(search || statusFilter !== 'All' || roleFilter !== 'All') && (
              <div className="flex items-end pb-[2px]">
                <button 
                  onClick={() => {
                    setSearch('');
                    setStatusFilter('All');
                    setRoleFilter('All');
                  }} 
                  className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors flex items-center gap-1.5 bg-indigo-50/80 px-4 h-10 rounded-xl hover:bg-indigo-100 uppercase tracking-wider"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <span>Clear</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Table */}
        <div className={`overflow-x-auto transition-opacity duration-200 ${isRefetching ? 'opacity-70' : 'opacity-100'}`}>
          {isLoading ? (
            <div className="p-6">
              <TableSkeleton rows={5} />
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-16 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
                      <p className="mt-1 text-sm text-gray-500">Try adjusting your filters or search query.</p>
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                              {user.name.charAt(0)}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-medium">
                          {user.current_role ? user.current_role.display_name : <span className="text-gray-400 italic font-normal">None</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {renderStatusBadge(user.account_status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(user.joined_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {user.id !== currentUser?.id && user.assignable_roles && user.assignable_roles.length > 0 && (
                          <div className="flex justify-end gap-3">
                            {user.account_status === 'PENDING_APPROVAL' || !user.current_role ? (
                              <button
                                onClick={() => setSelectedUserForAssign(user)}
                                className="text-teal-600 hover:text-teal-900 font-semibold"
                              >
                                Assign Role
                              </button>
                            ) : (
                              <>
                                <button
                                  onClick={() => setSelectedUserForAssign(user)}
                                  className="text-teal-600 hover:text-teal-900 font-semibold"
                                >
                                  Change Role
                                </button>
                                <button
                                  onClick={() => setSelectedUserForRemove(user)}
                                  className="text-red-600 hover:text-red-900 font-semibold"
                                >
                                  Remove Role
                                </button>
                              </>
                            )}
                          </div>
                        )}
                        {user.id !== currentUser?.id && (!user.assignable_roles || user.assignable_roles.length === 0) && (
                          <span className="text-gray-400 italic text-xs">No permissions</span>
                        )}
                        {user.id === currentUser?.id && (
                           <span className="text-gray-400 italic text-xs">It's you</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </Card>

      {selectedUserForAssign && (
        <AssignRoleModal
          user={selectedUserForAssign}
          isOpen={true}
          onClose={() => setSelectedUserForAssign(null)}
          onAssign={handleAssignRole}
        />
      )}

      {selectedUserForRemove && (
        <RemoveRoleModal
          user={selectedUserForRemove}
          isOpen={true}
          onClose={() => setSelectedUserForRemove(null)}
          onRemove={handleRemoveRole}
        />
      )}
    </PageContainer>
  );
};
