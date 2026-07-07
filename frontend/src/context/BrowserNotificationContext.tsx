import React, { createContext, useContext, useState, useEffect } from 'react';
import { browserNotificationService } from '../services/browserNotificationService';

interface BrowserNotificationContextType {
  permission: NotificationPermission;
  isSupported: boolean;
  canNotify: boolean;
  requestPermission: () => Promise<NotificationPermission>;
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

  const value = {
    permission,
    isSupported,
    canNotify: browserNotificationService.canNotify(),
    requestPermission,
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
