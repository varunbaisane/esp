import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Notification } from '../../types/notification';
import { useAppNotifications } from '../../context/AppNotificationContext';
import { getNotificationLink } from '../../utils/notificationNavigation';

interface NotificationItemProps {
  notification: Notification;
}

const getRelativeTime = (dateStr: string) => {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
};

export const NotificationItem: React.FC<NotificationItemProps> = ({ notification }) => {
  const navigate = useNavigate();
  const { markAsRead } = useAppNotifications();

  const handleClick = async () => {
    // Navigate immediately if possible
    const link = getNotificationLink(notification.entity_type, notification.entity_id);
    if (link) {
      navigate(link);
    }
    
    // Mark as read in background if unread
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
  };

  const getActorIcon = () => {
    if (notification.actor_id) {
      // In a real app we'd fetch the user's avatar or use a robust avatar component
      return <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">U</div>;
    }
    // System notification
    return (
      <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-600">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11V7a4 4 0 018 0v4c0 1.258.2 2.472.571 3.611l.054.09A14.013 14.013 0 0112 20.571" />
        </svg>
      </div>
    );
  };

  return (
    <div
      onClick={handleClick}
      className={`p-4 flex gap-4 items-start cursor-pointer transition-colors border-b border-slate-100 last:border-0 hover:bg-slate-50 ${
        !notification.is_read ? 'bg-teal-50/50' : ''
      }`}
    >
      <div className="flex-shrink-0">
        {getActorIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900 mb-1">
          {notification.title}
        </p>
        <p className="text-sm text-slate-600 line-clamp-2">
          {notification.message}
        </p>
        <p className="text-xs text-slate-400 mt-2">
          {getRelativeTime(notification.created_at)}
        </p>
      </div>
      
      {!notification.is_read && (
        <div className="flex-shrink-0 mt-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
        </div>
      )}
    </div>
  );
};
