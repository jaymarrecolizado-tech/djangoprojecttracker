"""Models for audit app."""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Model for audit logs."""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    class Meta:
        db_table = 'audit_auditlog'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} {self.model_name} at {self.created_at}"

    @property
    def changes(self):
        """Get the changes between old and new values."""
        if not self.old_values and not self.new_values:
            return {}
        
        changes = {}
        all_keys = set(self.old_values.keys()) | set(self.new_values.keys())
        
        for key in all_keys:
            old_val = self.old_values.get(key)
            new_val = self.new_values.get(key)
            if old_val != new_val:
                changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return changes
