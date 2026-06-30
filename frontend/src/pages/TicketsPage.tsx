import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ticketService } from "../services/ticketService";
import type { TicketSummary, TicketFilters as FiltersType } from "../types/ticket";
import { TicketTable } from "../components/tickets/TicketTable";
import { TicketFilters } from "../components/tickets/TicketFilters";
import { TicketPagination } from "../components/tickets/TicketPagination";
import { StateMessage } from "../components/common/StateMessage";
import { TableSkeleton } from "../components/common/TableSkeleton";
import { PageContainer } from "../components/layout/PageContainer";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { DEFAULT_PAGE_SIZE } from "../types/ticket";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export const TicketsPage = () => {
  useDocumentTitle("Tickets");
  const [searchParams, setSearchParams] = useSearchParams();
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const currentPage = parseInt(searchParams.get("page") || "1", 10);
  const sortBy = searchParams.get("sort_by") || "created_at";
  const sortOrder = (searchParams.get("sort_order") || "desc") as "asc" | "desc";
  
  const filters: FiltersType = {
    status: searchParams.get("status") || undefined,
    priority: searchParams.get("priority") || undefined,
    level: searchParams.get("level") || undefined,
    assigned_to: searchParams.get("assigned_to") || undefined,
    sla_status: searchParams.get("sla_status") || undefined,
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined);

  useEffect(() => {
    const fetchTickets = async () => {
      setLoading(true);
      setError(null);
      try {
        const offset = (currentPage - 1) * DEFAULT_PAGE_SIZE;
        const data = await ticketService.getTickets(
          filters,
          DEFAULT_PAGE_SIZE,
          offset,
          sortBy,
          sortOrder
        );
        setTickets(data.items);
        setTotal(data.total);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message || "Unable to connect to backend while fetching tickets.");
        } else {
          setError("Unable to connect to backend while fetching tickets.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, [searchParams]);

  const handleFilterChange = (newFilters: FiltersType) => {
    const params = new URLSearchParams(searchParams);
    
    // Clear all existing filter params
    params.delete("status");
    params.delete("priority");
    params.delete("level");
    params.delete("assigned_to");
    params.delete("sla_status");
    
    // Reset to page 1 on filter change
    params.delete("page");

    // Add new filters
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    setSearchParams(params);
  };

  const handleSort = (column: string) => {
    const params = new URLSearchParams(searchParams);
    if (sortBy === column) {
      // Toggle order
      params.set("sort_order", sortOrder === "asc" ? "desc" : "asc");
    } else {
      params.set("sort_by", column);
      params.set("sort_order", "asc"); // Default to asc when switching columns
    }
    setSearchParams(params);
  };

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams);
    if (page === 1) {
      params.delete("page");
    } else {
      params.set("page", page.toString());
    }
    setSearchParams(params);
  };

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Tickets</h2>
          <p className="mt-2 text-sm text-gray-500">Browse and manage all engineering support tickets.</p>
        </div>
        <Button
          to="/tickets/new"
          variant="primary"
        >
          <span className="text-xl mr-1 leading-none">+</span> <span className="font-semibold">Create Ticket</span>
        </Button>
      </div>

      <TicketFilters filters={filters} onChange={handleFilterChange} />

      {!loading && !error && (
        <div className="mb-4 text-sm font-medium text-gray-600 px-1">
          Showing <span className="font-bold text-gray-900">{tickets.length}</span> of <span className="font-bold text-gray-900">{total}</span> ticket{total !== 1 ? 's' : ''} {hasActiveFilters ? 'with applied criteria' : ''}
        </div>
      )}

      {error ? (
        <StateMessage 
          title="Unable to load tickets" 
          message={error} 
          type="error" 
          onRetry={() => window.location.reload()}
        />
      ) : loading ? (
        <Card noPadding>
          <TableSkeleton rows={10} />
        </Card>
      ) : (
        <Card noPadding>
          <TicketTable 
            tickets={tickets} 
            sortBy={sortBy} 
            sortOrder={sortOrder} 
            onSort={handleSort} 
          />
        </Card>
      )}

      <TicketPagination
        currentPage={currentPage}
        totalItems={total}
        limit={DEFAULT_PAGE_SIZE}
        onPageChange={handlePageChange}
        isLoading={loading}
      />
    </PageContainer>
  );
};
