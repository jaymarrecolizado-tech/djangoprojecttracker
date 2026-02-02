"""
Project models for the Project Tracking Management System.

This module provides models for project type categorization and project site management.
"""

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedModel


class ProjectStatus(models.TextChoices):
    """Project status choices."""
    PENDING = 'pending', _('Pending')
    IN_PROGRESS = 'in_progress', _('In Progress')
    DONE = 'done', _('Done')
    CANCELLED = 'cancelled', _('Cancelled')
    ON_HOLD = 'on_hold', _('On Hold')


class ProjectType(models.Model):
    """
    Project Type model for categorizing projects.

    Attributes:
        name: Type name
        code_prefix: Prefix for project codes
        color_code: Color for UI representation
        description: Type description
        is_active: Whether this type is active
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Project type name')
    )
    code_prefix = models.CharField(
        max_length=10,
        unique=True,
        help_text=_('Prefix for project site codes')
    )
    color_code = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text=_('Hex color code for UI representation')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Type description')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this type is active')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for ProjectType model."""
        verbose_name = _('project type')
        verbose_name_plural = _('project types')
        ordering = ['name']
        db_table = 'projects_project_type'

    def __str__(self) -> str:
        """Return string representation of the project type."""
        return self.name

    @property
    def project_count(self) -> int:
        """Get the number of projects of this type."""
        return self.projects.filter(is_deleted=False).count()


class ProjectSite(TimestampedModel):
    """
    Project Site model for tracking project locations.

    This is the main model for project tracking, containing all information
    about a project site including its location, status, and metadata.

    Attributes:
        site_code: Unique project site code
        project_type: Type of project
        site_name: Project site name
        barangay: Barangay location
        municipality: Municipality location
        province: Province location
        location: Geographic point location
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        activation_date: Project activation date
        status: Current project status
        remarks: Additional remarks
        metadata: JSON metadata
        created_by: User who created the project
        updated_by: User who last updated the project
        is_deleted: Soft delete flag
    """

    site_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Unique project site code')
    )
    project_type = models.ForeignKey(
        ProjectType,
        on_delete=models.PROTECT,
        related_name='projects',
        help_text=_('Project type')
    )
    site_name = models.CharField(
        max_length=200,
        help_text=_('Project site name')
    )

    # Location hierarchy
    barangay = models.ForeignKey(
        'locations.Barangay',
        on_delete=models.PROTECT,
        related_name='projects',
        help_text=_('Barangay location')
    )
    municipality = models.ForeignKey(
        'locations.Municipality',
        on_delete=models.PROTECT,
        related_name='projects',
        help_text=_('Municipality location')
    )
    province = models.ForeignKey(
        'locations.Province',
        on_delete=models.PROTECT,
        related_name='projects',
        help_text=_('Province location')
    )

    # Geographic location
    location = gis_models.PointField(
        srid=4326,
        spatial_index=True,
        help_text=_('Geographic location (longitude, latitude)')
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        help_text=_('Latitude coordinate')
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        help_text=_('Longitude coordinate')
    )

    # Project details
    activation_date = models.DateField(
        help_text=_('Project activation date')
    )
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PENDING,
        db_index=True,
        help_text=_('Current project status')
    )
    remarks = models.TextField(
        blank=True,
        help_text=_('Additional remarks')
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional metadata as JSON')
    )

    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='projects_created',
        null=True,
        help_text=_('User who created the project')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='projects_updated',
        null=True,
        help_text=_('User who last updated the project')
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Soft delete flag')
    )

    class Meta:
        """Meta options for ProjectSite model."""
        verbose_name = _('project site')
        verbose_name_plural = _('project sites')
        ordering = ['-created_at']
        db_table = 'projects_project_site'
        indexes = [
            models.Index(fields=['status', 'is_deleted']),
            models.Index(fields=['project_type', 'is_deleted']),
            models.Index(fields=['province', 'is_deleted']),
            models.Index(fields=['municipality', 'is_deleted']),
            models.Index(fields=['barangay', 'is_deleted']),
        ]

    def __str__(self) -> str:
        """Return string representation of the project site."""
        return f"{self.site_code} - {self.site_name}"

    @property
    def status_color(self) -> str:
        """Get the color code for the current status."""
        status_colors = {
            ProjectStatus.PENDING: '#F59E0B',
            ProjectStatus.IN_PROGRESS: '#3B82F6',
            ProjectStatus.DONE: '#10B981',
            ProjectStatus.CANCELLED: '#EF4444',
            ProjectStatus.ON_HOLD: '#6B7280',
        }
        return status_colors.get(self.status, '#6B7280')

    @property
    def location_address(self) -> str:
        """Get the full location address."""
        return f"{self.barangay.name}, {self.municipality.name}, {self.province.name}"

    def save(self, *args, **kwargs):
        """Override save to ensure location point matches lat/lng."""
        from django.contrib.gis.geos import Point

        # Update location point from lat/lng
        if self.latitude and self.longitude:
            self.location = Point(
                float(self.longitude),
                float(self.latitude),
                srid=4326
            )

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False, deleted_by=None):
        """Soft delete the project site."""
        from django.utils import timezone

        self.is_deleted = True
        self.updated_at = timezone.now()
        self.updated_by = deleted_by
        self.save(update_fields=['is_deleted', 'updated_at', 'updated_by'])

    def restore(self, restored_by=None):
        """Restore a soft-deleted project site."""
        from django.utils import timezone

        self.is_deleted = False
        self.updated_at = timezone.now()
        self.updated_by = restored_by
        self.save(update_fields=['is_deleted', 'updated_at', 'updated_by'])


class ProjectStatusHistory(TimestampedModel):
    """
    Project Status History model for tracking status changes.

    This model maintains an audit trail of all status changes for a project.

    Attributes:
        project: The project whose status changed
        old_status: Previous status
        new_status: New status
        reason: Reason for the status change
        changed_by: User who made the change
    """

    project = models.ForeignKey(
        ProjectSite,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text=_('The project whose status changed')
    )
    old_status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        help_text=_('Previous status')
    )
    new_status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        help_text=_('New status')
    )
    reason = models.TextField(
        blank=True,
        help_text=_('Reason for the status change')
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes',
        help_text=_('User who made the change')
    )

    class Meta:
        """Meta options for ProjectStatusHistory model."""
        verbose_name = _('project status history')
        verbose_name_plural = _('project status histories')
        ordering = ['-created_at']
        db_table = 'projects_status_history'

    def __str__(self) -> str:
        """Return string representation of the status history entry."""
        return f"{self.project.site_code}: {self.old_status} -> {self.new_status}"
