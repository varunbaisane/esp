import React from 'react';
import { useAppNotifications } from '../../context/AppNotificationContext';
import { NotificationItem } from './NotificationItem';
import { NotificationSkeleton } from './NotificationSkeleton';
import { StateMessage } from '../common/StateMessage';

interface NotificationDropdownProps {
  onClose: () => void;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = () => {
  const { notifications, unreadCount, loading, markAllAsRead } = useAppNotifications();

  return (
    <div className="fixed sm:absolute left-4 right-4 sm:left-auto sm:right-0 top-20 sm:top-auto sm:mt-2 sm:w-96 bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden z-[100]">
      <div className="flex items-center justify-between p-4 border-b border-slate-200">
        <h3 className="font-semibold text-slate-900">Notifications</h3>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            Mark all as read
          </button>
        )}
      </div>

      <div className="max-h-[400px] overflow-y-auto">
        {loading ? (
          <NotificationSkeleton />
        ) : notifications.length === 0 ? (
          <div className="p-4">
            <StateMessage
              title="You're all caught up"
              message="No notifications yet."
              type="empty"
            />
          </div>
        ) : (
          <div>
            {notifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
