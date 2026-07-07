import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BrowserNotificationService } from './browserNotificationService';

describe('BrowserNotificationService', () => {
  let service: BrowserNotificationService;

  beforeEach(() => {
    service = new BrowserNotificationService();
    // Reset global Notification object
    if (globalThis.window) {
      // @ts-ignore
      delete globalThis.window.Notification;
    }
  });

  it('handles unsupported browser gracefully', () => {
    // Window exists but no Notification API
    // @ts-ignore
    globalThis.window = {};
    
    expect(service.isSupported()).toBe(false);
    expect(service.permission).toBe('denied');
    expect(service.canNotify()).toBe(false);
  });

  it('detects supported browser', () => {
    // @ts-ignore
    globalThis.window = { Notification: { permission: 'default' } };
    
    expect(service.isSupported()).toBe(true);
    expect(service.permission).toBe('default');
  });

  it('returns true for canNotify when permission is granted', () => {
    // @ts-ignore
    globalThis.window = { Notification: { permission: 'granted' } };
    
    expect(service.canNotify()).toBe(true);
  });

  it('requests permission if supported', async () => {
    const requestPermissionMock = vi.fn().mockResolvedValue('granted');
    // @ts-ignore
    globalThis.window = {
      Notification: { 
        permission: 'default',
        requestPermission: requestPermissionMock
      } as any
    } as any;
    
    const result = await service.requestPermission();
    expect(result).toBe('granted');
    expect(requestPermissionMock).toHaveBeenCalled();
  });

  it('silently returns denied when requesting permission on unsupported browser', async () => {
    // @ts-ignore
    globalThis.window = {};
    
    const result = await service.requestPermission();
    expect(result).toBe('denied');
  });
});
