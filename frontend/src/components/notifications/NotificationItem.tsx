import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { 
  Bell, 
  AlertCircle, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Trash2 
} from 'lucide-react';
import type { Notification } from '@/types/api';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: number) => void;
  onDelete: (id: number) => void;
}

const notificationIcons = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertCircle,
};

const iconColors = {
  info: 'text-blue-500 bg-blue-50',
  success: 'text-green-500 bg-green-50',
  warning: 'text-amber-500 bg-amber-50',
  error: 'text-red-500 bg-red-50',
};

export function NotificationItem({ 
  notification, 
  onMarkAsRead, 
  onDelete 
}: NotificationItemProps) {
  const navigate = useNavigate();
  const [showDetails, setShowDetails] = useState(false);
  
  const Icon = notificationIcons[notification.notification_type] || Bell;
  const iconClass = iconColors[notification.notification_type] || 'text-gray-500 bg-gray-50';
  const timeAgo = formatDistanceToNow(new Date(notification.created_at), { addSuffix: true });

  const handleClick = () => {
    if (!notification.is_read) {
      onMarkAsRead(notification.id);
    }
    
    // Handle navigation based on notification data
    if (notification.data && typeof notification.data === 'object') {
      const data = notification.data as Record<string, unknown>;
      if (data.route) {
        navigate(data.route as string);
      } else if (data.project_id) {
        navigate(`/projects/${data.project_id}`);
      }
    }
  };

  return (
    <div 
      className={cn(
        'relative flex gap-3 p-3 rounded-lg transition-colors cursor-pointer',
        notification.is_read 
          ? 'bg-background hover:bg-accent' 
          : 'bg-primary/5 hover:bg-primary/10'
      )}
      onClick={handleClick}
    >
      {/* Icon */}
      <div className={cn('flex-shrink-0 rounded-full p-2', iconClass)}>
        <Icon className="h-4 w-4" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn(
            'text-sm font-medium line-clamp-1',
            notification.is_read ? 'text-foreground' : 'text-foreground'
          )}>
            {notification.title}
          </p>
          {!notification.is_read && (
            <span className="flex-shrink-0 h-2 w-2 rounded-full bg-primary" />
          )}
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">
          {notification.message}
        </p>
        
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-muted-foreground">
            {timeAgo}
          </span>
          
          {/* Actions */}
          <div 
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1"
          >
            {!notification.is_read && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
                onClick={() => onMarkAsRead(notification.id)}
              >
                Mark as read
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(notification.id);
              }}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Show additional data if available */}
        {showDetails && notification.data && (
          <div className="mt-2 p-2 bg-accent rounded text-xs font-mono overflow-x-auto">
            <pre>{JSON.stringify(notification.data, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
