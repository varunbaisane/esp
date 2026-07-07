import React, { createContext, useContext, useState, useEffect } from 'react';
import { browserNotificationService } from '../services/browserNotificationService';

import type { Notification } from '../types/notification';

interface BrowserNotificationContextType {
  permission: NotificationPermission;
  isSupported: boolean;
  canNotify: boolean;
  requestPermission: () => Promise<NotificationPermission>;
  showBrowserNotification: (notification: Notification, onClick?: () => void) => void;
}

const BrowserNotificationContext = createContext<BrowserNotificationContextType | undefined>(undefined);

export const BrowserNotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  
  const isSupported = browserNotificationService.isSupported();

  useEffect(() => {
    // Read the current permission on mount without prompting the user.
    setPermission(browserNotificationService.permission);
  }, []);

  const requestPermission = async () => {
    const newPermission = await browserNotificationService.requestPermission();
    setPermission(newPermission);
    return newPermission;
  };

  const showBrowserNotification = (notification: Notification, onClick?: () => void) => {
    browserNotificationService.showNotification(
      notification.title,
      {
        body: notification.message,
        tag: notification.id.toString(), // Prevents duplicate popups of the same ID
        // icon: '/logo.png', // Add if there is a logo later
      },
      onClick
    );
  };

  const value = {
    permission,
    isSupported,
    canNotify: browserNotificationService.canNotify(),
    requestPermission,
    showBrowserNotification,
  };

  return (
    <BrowserNotificationContext.Provider value={value}>
      {children}
    </BrowserNotificationContext.Provider>
  );
};

export const useBrowserNotification = () => {
  const context = useContext(BrowserNotificationContext);
  if (context === undefined) {
    throw new Error('useBrowserNotification must be used within a BrowserNotificationProvider');
  }
  return context;
};
