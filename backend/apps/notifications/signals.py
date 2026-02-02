"""Signals for notifications app."""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.projects.models import ProjectSite, ProjectStatusHistory
from .services import NotificationService


@receiver(pre_save, sender=ProjectSite)
def capture_old_status(sender, instance, **kwargs):
    """Capture the old status before saving."""
    if instance.pk:
        try:
            old_instance = ProjectSite.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_instance = old_instance
        except ProjectSite.DoesNotExist:
            instance._old_status = None
            instance._old_instance = None
    else:
        instance._old_status = None
        instance._old_instance = None


@receiver(post_save, sender=ProjectSite)
def project_status_changed(sender, instance, created, **kwargs):
    """Create notification when project status changes."""
    if created:
        # New project created
        NotificationService.create_project_notification(
            project=instance,
            notification_type='project_created'
        )
    else:
        # Check if status changed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            # Create status history record
            ProjectStatusHistory.objects.create(
                project=instance,
                old_status=old_status,
                new_status=instance.status,
                changed_by=instance.updated_by
            )
            
            # Create notification
            NotificationService.create_project_notification(
                project=instance,
                notification_type='status_changed'
            )


@receiver(post_save, sender=ProjectSite)
def project_updated(sender, instance, created, **kwargs):
    """Create notification when project is updated (but not status change)."""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        # Only create update notification if it's not a status change
        if not old_status or old_status == instance.status:
            # Create update notification
            if instance.updated_by and instance.created_by:
                NotificationService.create_notification(
                    user=instance.created_by,
                    notification_type='project_updated',
                    title='Project Updated',
                    message=f'Project "{instance.site_name}" ({instance.site_code}) has been updated.',
                    data={
                        'project_id': str(instance.id),
                        'project_code': instance.site_code,
                        'project_name': instance.site_name,
                        'updated_by': str(instance.updated_by.id) if instance.updated_by else None,
                        'action': 'updated'
                    }
                )
