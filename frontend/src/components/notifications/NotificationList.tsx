import { Link } from 'react-router-dom';
import { CheckCheck, Trash2, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { NotificationItem } from './NotificationItem';
import type { Notification } from '@/types/api';

interface NotificationListProps {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  isConnected: boolean;
  onMarkAsRead: (id: number) => void;
  onMarkAllAsRead: () => void;
  onDelete: (id: number) => void;
}

export function NotificationList({
  notifications,
  unreadCount,
  isLoading,
  isConnected,
  onMarkAsRead,
  onMarkAllAsRead,
  onDelete,
}: NotificationListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-3 p-3">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
        <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-3">
          <Bell className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium">No notifications</p>
        <p className="text-xs text-muted-foreground mt-1">
          You're all caught up!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">Notifications</span>
          {unreadCount > 0 && (
            <span className="h-5 px-1.5 rounded-full bg-primary text-primary-foreground text-xs font-medium">
              {unreadCount}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {/* Connection status indicator */}
          <div 
            className={`h-2 w-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-gray-300'
            }`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 px-2 text-xs"
              onClick={onMarkAllAsRead}
            >
              <CheckCheck className="h-3 w-3 mr-1" />
              Mark all read
            </Button>
          )}
        </div>
      </div>

      {/* Notification list */}
      <div className="max-h-96 overflow-y-auto">
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onMarkAsRead={onMarkAsRead}
            onDelete={onDelete}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="p-2 border-t">
        <Link
          to="/notifications"
          className="block w-full text-center text-sm text-primary hover:underline"
        >
          View all notifications
        </Link>
      </div>
    </div>
  );
}
