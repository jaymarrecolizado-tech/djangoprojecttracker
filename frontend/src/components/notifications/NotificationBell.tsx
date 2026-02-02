import { useState } from 'react';
import { Bell, Wifi, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useNotificationsManager } from '@/hooks/useNotifications';
import { NotificationList } from './NotificationList';
import { cn } from '@/lib/utils';

interface NotificationBellProps {
  className?: string;
}

export function NotificationBell({ className }: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const {
    notifications,
    unreadCount,
    isLoading,
    isConnected,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotificationsManager();

  const handleMarkAsRead = async (id: number) => {
    await markAsRead(id);
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const handleDelete = async (id: number) => {
    await deleteNotification(id);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="icon" 
          className={cn('relative', className)}
        >
          {isConnected ? (
            <Bell className="h-5 w-5" />
          ) : (
            <WifiOff className="h-5 w-5 text-muted-foreground" />
          )}
          {unreadCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-80 p-0">
        <NotificationList
          notifications={notifications}
          unreadCount={unreadCount}
          isLoading={isLoading}
          isConnected={isConnected}
          onMarkAsRead={handleMarkAsRead}
          onMarkAllAsRead={handleMarkAllAsRead}
          onDelete={handleDelete}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
