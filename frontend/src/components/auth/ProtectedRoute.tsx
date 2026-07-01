import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, currentUser } = useAuth();

  if (isLoading) {
    // Return null or a subtle spinner to avoid flashing unauthenticated state
    // before the redirect happens, or wait for context to resolve.
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (currentUser && currentUser.can_access_application === false) {
    return <Navigate to="/pending-approval" replace />;
  }

  return <>{children}</>;
};
