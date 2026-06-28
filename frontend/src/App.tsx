import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { PageLoader } from "./components/common/PageLoader";

const DashboardPage = lazy(() => import("./pages/DashboardPage").then(module => ({ default: module.DashboardPage })));
const TeamOperationsPage = lazy(() => import("./pages/TeamOperationsPage").then(module => ({ default: module.TeamOperationsPage })));
const PersonalWorkspacePage = lazy(() => import("./pages/PersonalWorkspacePage").then(module => ({ default: module.PersonalWorkspacePage })));
const TicketsPage = lazy(() => import("./pages/TicketsPage").then(module => ({ default: module.TicketsPage })));
const CreateTicketPage = lazy(() => import("./pages/CreateTicketPage").then(module => ({ default: module.CreateTicketPage })));
const TicketDetailPage = lazy(() => import("./pages/TicketDetailPage").then(module => ({ default: module.TicketDetailPage })));
const ActivityPage = lazy(() => import("./pages/ActivityPage").then(module => ({ default: module.ActivityPage })));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage").then(module => ({ default: module.AnalyticsPage })));
const LoginPage = lazy(() => import("./pages/auth/LoginPage").then(module => ({ default: module.LoginPage })));
const RegisterPage = lazy(() => import("./pages/auth/RegisterPage").then(module => ({ default: module.RegisterPage })));
const RegistrationSuccessPage = lazy(() => import("./pages/auth/RegistrationSuccessPage").then(module => ({ default: module.RegistrationSuccessPage })));
const VerifyEmailPage = lazy(() => import("./pages/auth/VerifyEmailPage").then(module => ({ default: module.VerifyEmailPage })));
const ForgotPasswordPage = lazy(() => import("./pages/auth/ForgotPasswordPage").then(module => ({ default: module.ForgotPasswordPage })));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/registration-success" element={<RegistrationSuccessPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />

          {/* Protected Portal Routes */}
          <Route path="/*" element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoader />}>
                  <Routes>
                    <Route path="/" element={<Navigate to="/workspace" replace />} />
                    <Route path="/workspace" element={<PersonalWorkspacePage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/team-operations" element={<TeamOperationsPage />} />
                    <Route path="/tickets" element={<TicketsPage />} />
                    <Route path="/tickets/new" element={<CreateTicketPage />} />
                    <Route path="/tickets/:id" element={<TicketDetailPage />} />
                    <Route path="/activity" element={<ActivityPage />} />
                    <Route path="/analytics" element={<AnalyticsPage />} />
                  </Routes>
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          } />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
