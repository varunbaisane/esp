
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { AuthLayout } from "../components/auth/AuthLayout";
import { Button } from "../components/common/Button";

export const PendingApprovalPage = () => {
  const { currentUser, isAuthenticated, isLoading, refreshStatus, logout } = useAuth();
  const navigate = useNavigate();

  // Redirect if not authenticated at all
  if (!isLoading && (!isAuthenticated || !currentUser)) {
    return <Navigate to="/login" replace />;
  }

  // If they somehow got here but actually have access, redirect to workspace
  if (!isLoading && currentUser?.can_access_application) {
    return <Navigate to="/workspace" replace />;
  }

  const handleRefresh = async () => {
    await refreshStatus();
    // Re-evaluating will happen automatically as currentUser updates
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (isLoading || !currentUser) {
    return null; // Return nothing or a spinner while loading
  }

  return (
    <AuthLayout
      title="Account Pending Approval"
      subtitle="Your account has been created successfully."
    >
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>

        <p className="text-sm text-gray-600 leading-relaxed text-left">
          An administrator or engineering manager must assign an engineering role before you can access the Engineering Support Platform.
        </p>
        <p className="text-sm text-gray-600 leading-relaxed text-left">
          Once your role has been assigned, simply refresh this page or sign in again.
        </p>

        <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 text-left space-y-3">
          <div>
            <span className="block text-xs font-medium text-gray-500 uppercase">Name</span>
            <span className="block text-sm font-medium text-gray-900">{currentUser.full_name}</span>
          </div>
          <div>
            <span className="block text-xs font-medium text-gray-500 uppercase">Email</span>
            <span className="block text-sm text-gray-700">{currentUser.email}</span>
          </div>
          <div>
            <span className="block text-xs font-medium text-gray-500 uppercase">Status</span>
            <div className="mt-1 flex items-center">
              <span className="h-2 w-2 rounded-full bg-blue-500 mr-2"></span>
              <span className="text-sm font-medium text-blue-700">Pending Approval</span>
            </div>
          </div>
        </div>

        <div className="pt-2 flex flex-col gap-3">
          <Button onClick={handleRefresh} variant="primary" className="w-full">
            Check Access
          </Button>
          <Button onClick={handleLogout} variant="secondary" className="w-full">
            Logout
          </Button>
        </div>
      </div>
    </AuthLayout>
  );
};
