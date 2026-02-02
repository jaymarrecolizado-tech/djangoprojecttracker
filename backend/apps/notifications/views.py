"""Views for notifications app."""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .services import NotificationService
from apps.common.responses import success_response, error_response
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notification CRUD operations."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List all notifications for the current user."""
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        
        result = NotificationService.get_user_notifications(
            user=request.user,
            page=int(page),
            page_size=int(page_size)
        )
        
        return success_response(data=result)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a single notification."""
        try:
            notification = self.get_object()
            serializer = self.get_serializer(notification)
            return success_response(data={'notification': serializer.data})
        except Notification.DoesNotExist:
            return error_response(message='Notification not found')
    
    def destroy(self, request, *args, **kwargs):
        """Delete a notification."""
        notification_id = kwargs.get('pk')
        if NotificationService.delete_notification(notification_id, request.user):
            return success_response(message='Notification deleted')
        return error_response(message='Notification not found')
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = NotificationService.get_unread_count(request.user)
        return success_response(data={'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = NotificationService.mark_all_as_read(request.user)
        return success_response(
            data={'marked_read': count},
            message=f'{count} notifications marked as read'
        )


class MarkAsReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        """Mark a specific notification as read."""
        if NotificationService.mark_as_read(notification_id, request.user):
            return success_response(message='Notification marked as read')
        return error_response(message='Notification not found')


class MarkAllReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Mark all notifications as read."""
        count = NotificationService.mark_all_as_read(request.user)
        return success_response(
            data={'marked_read': count},
            message=f'{count} notifications marked as read'
        )


class NotificationCountView(APIView):
    """Get notification counts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get notification counts."""
        total = Notification.objects.filter(user=request.user).count()
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        read = total - unread
        
        return success_response(data={
            'total': total,
            'unread': unread,
            'read': read
        })
