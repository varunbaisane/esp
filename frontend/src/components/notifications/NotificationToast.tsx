import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Notification } from '../../types/notification';
import { useAuth } from '../../hooks/useAuth';
import { getNotificationLink } from '../../utils/notificationNavigation';
import { notificationService } from '../../services/notificationService';

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

interface NotificationToastProps {
  notification: Notification;
  onDismiss: () => void;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({ notification, onDismiss }) => {
  const [isExiting, setIsExiting] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const isAdmin = currentUser?.roles?.includes('ADMIN') ?? false;

  const startTimer = () => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = window.setTimeout(() => {
      triggerDismiss();
    }, 5000);
  };

  const stopTimer = () => {
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const triggerDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss();
    }, 300); // match animation duration
  };

  const handleClick = async (e: React.MouseEvent) => {
    // If user clicked the close button, don't navigate
    if ((e.target as HTMLElement).closest('.toast-close-btn')) return;

    // Navigate immediately if possible
    const link = getNotificationLink(notification.entity_type, notification.entity_id, isAdmin);
    if (link) {
      navigate(link);
      triggerDismiss();
    }
    
    // Mark as read in background if unread
    if (!notification.is_read) {
      try {
        await notificationService.markAsRead(notification.id);
      } catch (err) {
        console.error('Failed to mark toast as read', err);
      }
    }
  };

  useEffect(() => {
    if (!isHovered) {
      startTimer();
    } else {
      stopTimer();
    }
    return stopTimer;
  }, [isHovered]);

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 
        transition-all duration-300 ease-in-out cursor-pointer hover:bg-slate-50
        ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
      `}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0 pt-0.5">
            <svg className="h-6 w-6 text-cyan-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0M3.124 7.5A8.969 8.969 0 015.292 3m13.416 0a8.969 8.969 0 012.168 4.5" />
            </svg>
          </div>
          <div className="ml-3 w-0 flex-1">
            <p className="text-sm font-medium text-gray-900">{notification.title}</p>
            <p className="mt-1 text-sm text-gray-500 line-clamp-2">{notification.message}</p>
            <p className="mt-1 text-xs text-gray-400">{getRelativeTime(notification.created_at)}</p>
          </div>
          <div className="ml-4 flex flex-shrink-0">
            <button
              type="button"
              className="toast-close-btn inline-flex rounded-md bg-transparent text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
              onClick={(e) => {
                e.stopPropagation();
                triggerDismiss();
              }}
            >
              <span className="sr-only">Close</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
