import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

interface AdminRouteProps {
  children: ReactNode;
}

export const AdminRoute = ({ children }: AdminRouteProps) => {
  const { currentUser, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  // Use the new currentUser object to check if they have admin or manager role
  // Since we don't have the new fields in AuthContext yet (we only updated the UsersAPI type, not the AuthContext type),
  // we might need to rely on the existing `roles` array in `currentUser` for the AdminRoute check.
  const hasAccess = currentUser?.roles?.some(role => 
    role === 'ADMIN' || role === 'ENGINEERING_MANAGER'
  );

  if (!hasAccess) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
