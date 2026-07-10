import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import type { Notification } from '../types/notification';
import { notificationService } from '../services/notificationService';
import { useAuth } from '../hooks/useAuth';
import { useNotification } from '../hooks/useNotification';
import { useBrowserNotification } from './BrowserNotificationContext';
import { useNotificationToast } from './NotificationToastContext';
import { notificationSoundService } from '../services/notificationSoundService';
import { useWebSocket } from './WebSocketContext';

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
  const { showBrowserNotification } = useBrowserNotification();
  const { showToast } = useNotificationToast();
  
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const unreadCountRef = useRef<number>(0);
  const refreshNotificationsRef = useRef<(() => Promise<void>) | null>(null);

  const refreshUnreadCount = useCallback(async (autoFetch = false) => {
    if (!isAuthenticated) return;
    try {
      const { unread_count } = await notificationService.getUnreadCount();
      
      if (autoFetch && unread_count > unreadCountRef.current) {
        if (refreshNotificationsRef.current) {
          refreshNotificationsRef.current();
        }
      }
      
      setUnreadCount(unread_count);
      unreadCountRef.current = unread_count;
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

      // Browser Notification & Toast Logic
      const lastSeenStr = localStorage.getItem('lastSeenNotificationId');
      let lastSeenId = lastSeenStr ? parseInt(lastSeenStr, 10) : 0;
      let maxNewId = lastSeenId;
      
      const newUnreadNotifications: Notification[] = [];

      for (const notification of data.notifications) {
        if (notification.id <= lastSeenId) break;

        if (!notification.is_read) {
          newUnreadNotifications.push(notification);
        }

        if (notification.id > maxNewId) {
          maxNewId = notification.id;
        }
      }

      if (newUnreadNotifications.length > 0) {
        // Dynamically import to avoid circular dependencies or cluttering top-level if not strictly needed,
        // though top-level import is fine. Assuming top-level import is available or we add it.
        try {
          const { notificationPreferenceService } = await import('../services/notificationPreferenceService');
          const preferences = await notificationPreferenceService.getPreferences();
          
          let playedSound = false;

          for (const notification of newUnreadNotifications) {
            const browserPref = preferences.find(p => p.notification_type === notification.type && p.channel === 'BROWSER');
            // If undefined, it might be a mandatory notification (e.g. WELCOME) which should always be delivered
            if (!browserPref || browserPref.enabled) {
              showBrowserNotification(notification);
            }

            const inAppPref = preferences.find(p => p.notification_type === notification.type && p.channel === 'IN_APP');
            if (!inAppPref || inAppPref.enabled) {
              showToast(notification);
              if (!playedSound) {
                notificationSoundService.play();
                playedSound = true;
              }
            }
          }
        } catch (prefError) {
          console.error("Failed to fetch preferences, falling back to showing all", prefError);
          for (const notification of newUnreadNotifications) {
            showBrowserNotification(notification);
            showToast(notification);
          }
          notificationSoundService.play();
        }
      }

      if (maxNewId > lastSeenId) {
        localStorage.setItem('lastSeenNotificationId', maxNewId.toString());
      }

    } catch (error) {
      console.error('Failed to fetch notifications', error);
      notify.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, refreshUnreadCount, notify, showBrowserNotification, showToast]);

  useEffect(() => {
    refreshNotificationsRef.current = refreshNotifications;
  }, [refreshNotifications]);

  const { isConnected, lastMessage } = useWebSocket();
  const wasConnectedRef = useRef(false);

  // Auto-refresh on connection/reconnection to catch missed notifications
  useEffect(() => {
    if (isConnected && !wasConnectedRef.current && isAuthenticated) {
      refreshNotifications();
    }
    wasConnectedRef.current = isConnected;
  }, [isConnected, isAuthenticated, refreshNotifications]);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'notification' && lastMessage.payload) {
      const notification = lastMessage.payload as Notification;
      
      // Prevent duplicates if already fetched
      setNotifications(prev => {
        if (prev.some(n => n.id === notification.id)) return prev;
        return [notification, ...prev];
      });

      setUnreadCount(prev => prev + 1);

      // We only process toasts/sounds for unread notifications, which fresh ones will be
      import('../services/notificationPreferenceService').then(({ notificationPreferenceService }) => {
        notificationPreferenceService.getPreferences().then(preferences => {
          let playedSound = false;

          const browserPref = preferences.find(p => p.notification_type === notification.type && p.channel === 'BROWSER');
          if (!browserPref || browserPref.enabled) {
            showBrowserNotification(notification);
          }

          const inAppPref = preferences.find(p => p.notification_type === notification.type && p.channel === 'IN_APP');
          if (!inAppPref || inAppPref.enabled) {
            showToast(notification);
            if (!playedSound) {
              notificationSoundService.play();
              playedSound = true;
            }
          }
        }).catch(err => {
          console.error("Failed to fetch preferences on ws event", err);
          showBrowserNotification(notification);
          showToast(notification);
          notificationSoundService.play();
        });
      });
    }
  }, [lastMessage, showBrowserNotification, showToast]);

  useEffect(() => {
    // Only refresh once on mount if authenticated and not yet connected to ws
    // (the websocket isConnected effect will handle the main refresh once connected)
    if (isAuthenticated && !wasConnectedRef.current) {
      refreshUnreadCount();
    }

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        refreshUnreadCount();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
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
