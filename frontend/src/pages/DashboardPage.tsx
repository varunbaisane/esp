import { useEffect, useState } from "react";
import { healthService } from "../services/healthService";
import { ticketService } from "../services/ticketService";
import type { TicketStats } from "../types/ticket";

export const DashboardPage = () => {
  const [healthStatus, setHealthStatus] = useState<string | null>(null);
  const [ticketStats, setTicketStats] = useState<TicketStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const health = await healthService.getHealth();
        setHealthStatus(health.status);

        const stats = await ticketService.getStats();
        setTicketStats(stats);
      } catch (err: any) {
        setError(err.message || "Failed to connect to backend");
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>Engineering Support Platform</h1>
      <h2>Frontend Connected</h2>
      
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      
      <div>
        <h3>Backend Status:</h3>
        <p>{healthStatus || "Connecting..."}</p>
      </div>

      {ticketStats && (
        <div>
          <h3>Ticket Stats:</h3>
          <ul>
            <li>Open: {ticketStats.open}</li>
            <li>In Progress: {ticketStats.in_progress}</li>
            <li>Resolved: {ticketStats.resolved}</li>
            <li>Closed: {ticketStats.closed}</li>
            <li>Total: {ticketStats.total}</li>
          </ul>
        </div>
      )}
    </div>
  );
};
