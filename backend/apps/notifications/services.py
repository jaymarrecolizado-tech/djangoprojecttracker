"""Services for notifications app."""
import json
import asyncio
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, data=None):
        """Create a new notification."""
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        
        # Send real-time notification via WebSocket
        NotificationService.send_notification_to_user(user, notification)
        
        return notification
    
    @staticmethod
    def create_bulk_notifications(notifications_data):
        """Create multiple notifications at once."""
        notifications = []
        for data in notifications_data:
            notification = Notification.objects.create(
                user=data['user'],
                notification_type=data['notification_type'],
                title=data['title'],
                message=data['message'],
                data=data.get('data', {})
            )
            notifications.append(notification)
            # Send real-time notification
            NotificationService.send_notification_to_user(data['user'], notification)
        
        return notifications
    
    @staticmethod
    def send_notification_to_user(user, notification):
        """Send notification to user via WebSocket."""
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        
        group_name = f"user_{user.id}"
        
        async def _send():
            await channel_layer.group_send(
                group_name,
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': str(notification.id),
                        'type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'data': notification.data,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
        
        try:
            async_to_sync(_send)()
        except Exception:
            # Silently fail if WebSocket is not available
            pass
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user."""
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    @staticmethod
    def delete_notification(notification_id, user):
        """Delete a notification."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_notifications(user, page=1, page_size=20):
        """Get paginated notifications for a user."""
        from django.core.paginator import Paginator
        
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        paginator = Paginator(notifications, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'notifications': list(page_obj.object_list.values()),
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    
    @staticmethod
    def create_project_notification(project, notification_type, created_by=None):
        """Create notification related to a project."""
        from apps.projects.models import ProjectStatus
        
        if notification_type == 'project_created':
            return NotificationService.create_notification(
                user=project.created_by if project.created_by else None,
                notification_type='project_created',
                title='New Project Created',
                message=f'Project "{project.site_name}" ({project.site_code}) has been created.',
                data={
                    'project_id': str(project.id),
                    'project_code': project.site_code,
                    'project_name': project.site_name,
                    'status': project.status,
                    'action': 'created'
                }
            )
        
        elif notification_type == 'status_changed':
            # Get the latest status history
            status_history = project.status_history.first()
            old_status = status_history.old_status if status_history else 'unknown'
            new_status = project.status
            
            return NotificationService.create_notification(
                user=project.created_by if project.created_by else None,
                notification_type='status_changed',
                title='Project Status Updated',
                message=f'Project "{project.site_name}" status changed from {old_status} to {new_status}.',
                data={
                    'project_id': str(project.id),
                    'project_code': project.site_code,
                    'project_name': project.site_name,
                    'old_status': old_status,
                    'new_status': new_status,
                    'action': 'status_changed'
                }
            )
        
        return None
