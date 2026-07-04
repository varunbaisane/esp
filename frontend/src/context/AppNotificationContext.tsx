import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { Notification } from '../types/notification';
import { notificationService } from '../services/notificationService';
import { useAuth } from '../hooks/useAuth';
import { useNotification } from '../hooks/useNotification';

interface AppNotificationContextProps {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  refreshNotifications: () => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
  markAsRead: (notificationId: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

const AppNotificationContext = createContext<AppNotificationContextProps | undefined>(undefined);

export const AppNotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const notify = useNotification();
  
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const refreshUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const { unread_count } = await notificationService.getUnreadCount();
      setUnreadCount(unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count', error);
    }
  }, [isAuthenticated]);

  const refreshNotifications = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const data = await notificationService.getNotifications(1, 20);
      setNotifications(data.notifications);
      await refreshUnreadCount();
    } catch (error) {
      console.error('Failed to fetch notifications', error);
      notify.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, refreshUnreadCount, notify]);

  useEffect(() => {
    // NodeJS.Timeout is not available in browser TS without types/node, use window.setInterval return type (number)
    let interval: number;

    const startPolling = () => {
      interval = window.setInterval(() => {
        if (document.visibilityState !== 'hidden') {
          refreshUnreadCount();
        }
      }, 30000);
    };

    if (isAuthenticated) {
      refreshUnreadCount();
      startPolling();
    }

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        refreshUnreadCount();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (interval) window.clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isAuthenticated, refreshUnreadCount]);

  const markAsRead = async (notificationId: number) => {
    const target = notifications.find((n) => n.id === notificationId);
    if (!target || target.is_read) return;

    const previousNotifications = [...notifications];
    const previousUnreadCount = unreadCount;

    setNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n))
    );
    setUnreadCount((prev) => Math.max(0, prev - 1));

    try {
      await notificationService.markAsRead(notificationId);
      refreshUnreadCount();
    } catch (error) {
      setNotifications(previousNotifications);
      setUnreadCount(previousUnreadCount);
      notify.error('Failed to mark notification as read');
    }
  };

  const markAllAsRead = async () => {
    if (unreadCount === 0) return;

    const previousNotifications = [...notifications];
    const previousUnreadCount = unreadCount;

    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);

    try {
      await notificationService.markAllAsRead();
      refreshUnreadCount();
    } catch (error) {
      setNotifications(previousNotifications);
      setUnreadCount(previousUnreadCount);
      notify.error('Failed to mark all notifications as read');
    }
  };

  return (
    <AppNotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        refreshNotifications,
        refreshUnreadCount,
        markAsRead,
        markAllAsRead,
      }}
    >
      {children}
    </AppNotificationContext.Provider>
  );
};

export const useAppNotifications = (): AppNotificationContextProps => {
  const context = useContext(AppNotificationContext);
  if (context === undefined) {
    throw new Error('useAppNotifications must be used within an AppNotificationProvider');
  }
  return context;
};
