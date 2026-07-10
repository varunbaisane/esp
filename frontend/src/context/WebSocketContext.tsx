import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';

interface WebSocketContextType {
  isConnected: boolean;
  lastMessage: any | null;
  reconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const MAX_RECONNECT_DELAY = 30000;

  const connect = useCallback(() => {
    if (!token || !isAuthenticated) return;

    // Clear any existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Determine WS URL based on current host
    // For local dev, Vite runs on 5173, backend on 8000. 
    // Assuming API_URL is handled via vite proxy or environment variable.
    // We'll use the VITE_API_URL if available, else derive from window.location
    const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.host}`;
    let wsBaseUrl = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    if (wsBaseUrl.endsWith('/api/v1')) {
      wsBaseUrl = wsBaseUrl.slice(0, -7);
    }
    
    const wsUrl = `${wsBaseUrl}/api/v1/ws/notifications?token=${token}`;
    
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0; // Reset attempts on successful connection
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (e) {
        console.error("Failed to parse WebSocket message", e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      
      // If not a clean close and we are still authenticated, attempt to reconnect
      if (isAuthenticated) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), MAX_RECONNECT_DELAY);
        reconnectAttemptsRef.current += 1;
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      // Let onclose handle the reconnection
    };

    wsRef.current = ws;
  }, [token, isAuthenticated]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, "User logged out");
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, connect, disconnect]);

  return (
    <WebSocketContext.Provider value={{ isConnected, lastMessage, reconnect: connect }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
