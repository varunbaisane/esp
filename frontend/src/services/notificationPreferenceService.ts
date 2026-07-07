import { apiClient } from '../api/client';
import type { NotificationPreference, NotificationPreferenceUpdate } from '../types/notificationPreference';

class NotificationPreferenceService {
  async getPreferences(): Promise<NotificationPreference[]> {
    const response = await apiClient.get('/notification-preferences/');
    return response.data;
  }

  async updatePreference(id: number, data: NotificationPreferenceUpdate): Promise<NotificationPreference> {
    const response = await apiClient.patch(`/notification-preferences/${id}`, data);
    return response.data;
  }
}

export const notificationPreferenceService = new NotificationPreferenceService();
