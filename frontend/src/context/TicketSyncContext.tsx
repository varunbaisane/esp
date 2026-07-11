import React, { createContext, useContext, useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from './WebSocketContext';
import { ticketService } from '../services/ticketService';

interface TicketSyncContextType {
  registerRefresh: (key: string, callback: () => void) => void;
  unregisterRefresh: (key: string) => void;
  // Specific for ticket detail which only refreshes for a particular ticket ID
  registerTicketRefresh: (ticketId: number, key: string, callback: () => void) => void;
  unregisterTicketRefresh: (ticketId: number, key: string) => void;
}

const TicketSyncContext = createContext<TicketSyncContextType | undefined>(undefined);

export const TicketSyncProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { lastMessage } = useWebSocket();
  const globalRefreshes = useRef<Map<string, () => void>>(new Map());
  const ticketRefreshes = useRef<Map<number, Map<string, () => void>>>(new Map());

  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === 'entity_updated' && lastMessage.payload?.entity_type === 'ticket') {
      const ticketId = lastMessage.payload.entity_id;
      
      // Invalidate the frontend cache so that subsequent GET requests fetch fresh data
      ticketService.invalidateCache(ticketId);
      
      // Trigger all global refreshes (e.g. Dashboard, Lists, Activity)
      globalRefreshes.current.forEach((callback) => {
        callback();
      });

      // Trigger specific ticket refreshes (e.g. Ticket Detail)
      if (ticketId) {
        const specificRefreshes = ticketRefreshes.current.get(ticketId);
        if (specificRefreshes) {
          specificRefreshes.forEach((callback) => {
            callback();
          });
        }
      }
    }
  }, [lastMessage]);

  const registerRefresh = useCallback((key: string, callback: () => void) => {
    globalRefreshes.current.set(key, callback);
  }, []);

  const unregisterRefresh = useCallback((key: string) => {
    globalRefreshes.current.delete(key);
  }, []);

  const registerTicketRefresh = useCallback((ticketId: number, key: string, callback: () => void) => {
    if (!ticketRefreshes.current.has(ticketId)) {
      ticketRefreshes.current.set(ticketId, new Map());
    }
    ticketRefreshes.current.get(ticketId)!.set(key, callback);
  }, []);

  const unregisterTicketRefresh = useCallback((ticketId: number, key: string) => {
    const specificRefreshes = ticketRefreshes.current.get(ticketId);
    if (specificRefreshes) {
      specificRefreshes.delete(key);
      if (specificRefreshes.size === 0) {
        ticketRefreshes.current.delete(ticketId);
      }
    }
  }, []);

  return (
    <TicketSyncContext.Provider value={{ registerRefresh, unregisterRefresh, registerTicketRefresh, unregisterTicketRefresh }}>
      {children}
    </TicketSyncContext.Provider>
  );
};

export const useTicketSync = () => {
  const context = useContext(TicketSyncContext);
  if (context === undefined) {
    throw new Error('useTicketSync must be used within a TicketSyncProvider');
  }
  return context;
};
