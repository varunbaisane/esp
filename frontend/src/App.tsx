import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { TeamOperationsPage } from "./pages/TeamOperationsPage";
import { PersonalWorkspacePage } from "./pages/PersonalWorkspacePage";
import { TicketsPage } from "./pages/TicketsPage";
import { CreateTicketPage } from "./pages/CreateTicketPage";
import { TicketDetailPage } from "./pages/TicketDetailPage";
import { ActivityPage } from "./pages/ActivityPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Portal Routes */}
          <Route path="/*" element={
            <ProtectedRoute>
              <AppLayout>
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
              </AppLayout>
            </ProtectedRoute>
          } />
        </Routes>
    </BrowserRouter>
  );
}

export default App;
