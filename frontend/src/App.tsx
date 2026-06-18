import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { TicketsPage } from "./pages/TicketsPage";
import { AppLayout } from "./components/layout/AppLayout";

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/tickets" element={<TicketsPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
