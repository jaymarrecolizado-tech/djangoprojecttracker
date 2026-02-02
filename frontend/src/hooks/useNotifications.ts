import { useQuery, useMutation, useQueryClient, useEffect, useCallback, useState } from '@tanstack/react-query';
import { notificationsService } from '@/services/notifications';
import { getWebSocketService, WebSocketStatus } from '@/services/websocket';
import type { Notification } from '@/types/api';
import type { NotificationListResponse } from '@/services/notifications';

const NOTIFICATIONS_QUERY_KEY = 'notifications';
const UNREAD_COUNT_QUERY_KEY = 'unread-count';

export interface NotificationFilters {
  is_read?: boolean;
  notification_type?: string;
  page?: number;
  page_size?: number;
}

export function useNotifications(filters?: NotificationFilters) {
  return useQuery({
    queryKey: [NOTIFICATIONS_QUERY_KEY, filters],
    queryFn: () => notificationsService.getNotifications(filters),
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useNotification(id: number) {
  return useQuery({
    queryKey: [NOTIFICATIONS_QUERY_KEY, id],
    queryFn: () => notificationsService.getNotification(id),
    enabled: !!id,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: [UNREAD_COUNT_QUERY_KEY],
    queryFn: () => notificationsService.getUnreadCount(),
    staleTime: 10 * 1000, // 10 seconds - check more frequently
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useMarkAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: number) => notificationsService.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [UNREAD_COUNT_QUERY_KEY] });
    },
  });
}

export function useMarkAllAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => notificationsService.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [UNREAD_COUNT_QUERY_KEY] });
    },
  });
}

export function useDeleteNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: number) => notificationsService.deleteNotification(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [UNREAD_COUNT_QUERY_KEY] });
    },
  });
}

export function useDeleteAllRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => notificationsService.deleteAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [UNREAD_COUNT_QUERY_KEY] });
    },
  });
}

/**
 * Hook for real-time notifications via WebSocket
 */
export function useRealTimeNotifications() {
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);

  const handleNotification = useCallback((notification: Notification) => {
    // Update notifications list with new notification
    queryClient.setQueryData<NotificationListResponse>(
      [NOTIFICATIONS_QUERY_KEY],
      (oldData: NotificationListResponse | undefined) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          results: [notification, ...oldData.results],
        };
      }
    );

    // Increment unread count
    queryClient.setQueryData<number>([UNREAD_COUNT_QUERY_KEY], (oldCount: number | undefined) => {
      return (oldCount || 0) + 1;
    });
  }, [queryClient]);

  const handleStatusChange = useCallback((status: string) => {
    setIsConnected(status === 'connected');
  }, []);

  useEffect(() => {
    const wsService = getWebSocketService();

    wsService.setCallbacks({
      onNotification: handleNotification,
      onStatusChange: handleStatusChange,
    });

    wsService.connect();

    return () => {
      wsService.disconnect();
    };
  }, [handleNotification, handleStatusChange]);

  return { isConnected };
}

/**
 * Hook for managing notification state and real-time updates
 */
export function useNotificationsManager() {
  const {
    data: notificationsData,
    isLoading,
    error,
    refetch,
  } = useNotifications({ page_size: 10 });

  const { data: unreadCount } = useUnreadCount();
  const markAsReadMutation = useMarkAsRead();
  const markAllAsReadMutation = useMarkAllAsRead();
  const deleteNotificationMutation = useDeleteNotification();
  const { isConnected } = useRealTimeNotifications();

  const markAsRead = async (notificationId: number) => {
    await markAsReadMutation.mutateAsync(notificationId);
  };

  const markAllAsRead = async () => {
    await markAllAsReadMutation.mutateAsync();
  };

  const deleteNotification = async (notificationId: number) => {
    await deleteNotificationMutation.mutateAsync(notificationId);
  };

  return {
    notifications: notificationsData?.results || [],
    unreadCount: unreadCount || 0,
    totalCount: notificationsData?.count || 0,
    isLoading,
    error,
    isConnected,
    refetch,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    isMarkingAsRead: markAsReadMutation.isPending,
    isMarkingAllAsRead: markAllAsReadMutation.isPending,
    isDeleting: deleteNotificationMutation.isPending,
  };
}
