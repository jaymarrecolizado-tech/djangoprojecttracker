"""Views for audit app."""
from rest_framework import viewsets
from apps.accounts.permissions import IsAdmin
from apps.common.responses import success_response
from .models import AuditLog

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs."""
    queryset = AuditLog.objects.select_related('user').order_by('-created_at')
    permission_classes = [IsAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = [{
            'id': log.id,
            'action': log.action,
            'model_name': log.model_name,
            'object_id': log.object_id,
            'user': log.user.full_name if log.user else 'System',
            'ip_address': log.ip_address,
            'created_at': log.created_at
        } for log in queryset[:100]]
        return success_response(data={'logs': data})
