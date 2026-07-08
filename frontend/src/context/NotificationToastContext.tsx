import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { Notification } from '../types/notification';
import { NotificationToast } from '../components/notifications/NotificationToast';

interface NotificationToastContextProps {
  showToast: (notification: Notification) => void;
  dismissToast: (id: number) => void;
}

const NotificationToastContext = createContext<NotificationToastContextProps | undefined>(undefined);

export const useNotificationToast = () => {
  const context = useContext(NotificationToastContext);
  if (!context) {
    throw new Error('useNotificationToast must be used within a NotificationToastProvider');
  }
  return context;
};

export const NotificationToastProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Notification[]>([]);
  const MAX_TOASTS = 3;

  const showToast = useCallback((notification: Notification) => {
    setToasts(prev => {
      // Prevent duplicates
      if (prev.some(t => t.id === notification.id)) return prev;
      
      const newToasts = [notification, ...prev];
      // Keep only up to MAX_TOASTS
      return newToasts.slice(0, MAX_TOASTS);
    });
  }, []);

  const dismissToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <NotificationToastContext.Provider value={{ showToast, dismissToast }}>
      {children}
      {/* Render Toast Queue */}
      <div 
        aria-live="assertive" 
        className="fixed inset-0 flex items-end px-4 py-6 pointer-events-none sm:p-6 z-50 justify-end flex-col gap-4"
      >
        <div className="flex w-full flex-col-reverse items-center gap-4 sm:items-end">
          {toasts.map(toast => (
            <NotificationToast
              key={toast.id}
              notification={toast}
              onDismiss={() => dismissToast(toast.id)}
            />
          ))}
        </div>
      </div>
    </NotificationToastContext.Provider>
  );
};
