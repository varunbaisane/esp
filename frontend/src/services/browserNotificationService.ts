export class BrowserNotificationService {
  /**
   * Check if the browser supports notifications
   */
  public isSupported(): boolean {
    return 'Notification' in window;
  }

  /**
   * Get current permission state gracefully
   */
  public get permission(): NotificationPermission {
    if (!this.isSupported()) {
      return 'denied';
    }
    return Notification.permission;
  }

  /**
   * Request permission from the user
   */
  public async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported()) {
      return 'denied';
    }
    
    // The browser will only prompt if it's currently 'default'
    return await Notification.requestPermission();
  }

  /**
   * Check if we are allowed to send notifications
   */
  public canNotify(): boolean {
    return this.isSupported() && this.permission === 'granted';
  }

  /**
   * Show a browser notification if permitted
   */
  public showNotification(title: string, options?: NotificationOptions): void {
    if (!this.canNotify()) {
      return;
    }
    
    new Notification(title, options);
  }
}

export const browserNotificationService = new BrowserNotificationService();
