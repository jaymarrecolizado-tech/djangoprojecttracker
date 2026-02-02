import apiClient from './api';
import type { ApiResponse, Notification } from '@/types/api';

/**
 * Notifications Service
 * 
 * Handles notification API operations.
 * Endpoints:
 * - GET /api/v1/notifications/ - List notifications
 * - GET /api/v1/notifications/{id}/ - Get notification
 * - POST /api/v1/notifications/{id}/read/ - Mark as read
 * - POST /api/v1/notifications/read-all/ - Mark all as read
 */

export interface NotificationListParams {
  page?: number;
  page_size?: number;
  is_read?: boolean;
  notification_type?: string;
}

export interface NotificationListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notification[];
  unread_count: number;
}

export interface NotificationFilters {
  is_read?: boolean;
  notification_type?: string;
  start_date?: string;
  end_date?: string;
}

export const notificationsService = {
  /**
   * Get list of notifications with pagination
   * @param params - Filter and pagination parameters
   * @returns Paginated list of notifications
   */
  async getNotifications(params?: NotificationListParams): Promise<NotificationListResponse> {
    const response = await apiClient.getInstance().get<ApiResponse<NotificationListResponse>>(
      'notifications/',
      { params }
    );
    return response.data.data;
  },

  /**
   * Get a single notification by ID
   * @param notificationId - Notification ID
   * @returns Notification details
   */
  async getNotification(notificationId: number): Promise<Notification> {
    const response = await apiClient.get<ApiResponse<Notification>>(`notifications/${notificationId}/`);
    return response.data;
  },

  /**
   * Mark a notification as read
   * @param notificationId - Notification ID
   * @returns Updated notification
   */
  async markAsRead(notificationId: number): Promise<Notification> {
    const response = await apiClient.post<ApiResponse<Notification>>(
      `notifications/${notificationId}/read/`
    );
    return response.data;
  },

  /**
   * Mark all notifications as read
   * @returns Success status
   */
  async markAllAsRead(): Promise<void> {
    await apiClient.post('notifications/read-all/');
  },

  /**
   * Delete a notification
   * @param notificationId - Notification ID
   */
  async deleteNotification(notificationId: number): Promise<void> {
    await apiClient.delete(`notifications/${notificationId}/`);
  },

  /**
   * Delete all read notifications
   * @returns Number of deleted notifications
   */
  async deleteAllRead(): Promise<number> {
    const response = await apiClient.delete<ApiResponse<{ deleted_count: number }>>('notifications/delete-read/');
    return response.data.deleted_count;
  },

  /**
   * Get unread notifications count
   * @returns Unread count
   */
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<ApiResponse<{ unread_count: number }>>('notifications/unread-count/');
    return response.data.unread_count;
  },

  /**
   * Get recent notifications (last 5 unread)
   * @returns List of recent notifications
   */
  async getRecentNotifications(): Promise<Notification[]> {
    const response = await this.getNotifications({ page_size: 5 });
    return response.results;
  },

  /**
   * Filter notifications by criteria
   * @param filters - Filter criteria
   * @returns List of filtered notifications
   */
  async filterNotifications(filters: NotificationFilters): Promise<Notification[]> {
    const response = await this.getNotifications({
      is_read: filters.is_read,
      notification_type: filters.notification_type,
    });
    return response.results;
  },
};

export default notificationsService;
