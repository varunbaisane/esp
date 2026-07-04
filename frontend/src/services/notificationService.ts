import { apiClient } from '../api/client';
import type { NotificationListResponse, UnreadCountResponse } from '../types/notification';

export const notificationService = {
  getNotifications: async (page: number = 1, pageSize: number = 20): Promise<NotificationListResponse> => {
    const response = await apiClient.get<NotificationListResponse>('/notifications', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    const response = await apiClient.get<UnreadCountResponse>('/notifications/unread-count');
    return response.data;
  },

  markAsRead: async (notificationId: number): Promise<void> => {
    await apiClient.patch(`/notifications/${notificationId}/read`);
  },

  markAllAsRead: async (): Promise<void> => {
    await apiClient.patch('/notifications/read-all');
  },
};
