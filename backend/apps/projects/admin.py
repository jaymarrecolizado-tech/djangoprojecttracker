"""
Admin configuration for the projects app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ProjectType, ProjectSite, ProjectStatusHistory


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    """Admin for ProjectType model."""

    list_display = ['name', 'code_prefix', 'color_code', 'project_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code_prefix']
    ordering = ['name']

    def project_count(self, obj):
        return obj.projects.filter(is_deleted=False).count()
    project_count.short_description = _('Projects')


class ProjectStatusHistoryInline(admin.TabularInline):
    """Inline for project status history."""
    model = ProjectStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'reason', 'changed_by', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProjectSite)
class ProjectSiteAdmin(admin.GISModelAdmin):
    """Admin for ProjectSite model."""

    list_display = [
        'site_code', 'site_name', 'project_type',
        'province', 'municipality', 'status', 'is_deleted'
    ]
    list_filter = [
        'status', 'project_type', 'province',
        'is_deleted', 'activation_date'
    ]
    search_fields = ['site_code', 'site_name', 'remarks']
    ordering = ['-created_at']
    inlines = [ProjectStatusHistoryInline]
    date_hierarchy = 'activation_date'

    fieldsets = (
        (None, {
            'fields': ('site_code', 'site_name', 'project_type')
        }),
        (_('Location'), {
            'fields': ('barangay', 'municipality', 'province', 'location')
        }),
        (_('Coordinates'), {
            'fields': ('latitude', 'longitude')
        }),
        (_('Details'), {
            'fields': ('activation_date', 'status', 'remarks', 'metadata')
        }),
        (_('Tracking'), {
            'fields': ('created_by', 'updated_by', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project_type', 'barangay', 'municipality', 'province'
        )


@admin.register(ProjectStatusHistory)
class ProjectStatusHistoryAdmin(admin.ModelAdmin):
    """Admin for ProjectStatusHistory model."""

    list_display = ['project', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['project__site_code', 'project__site_name', 'reason']
    readonly_fields = ['project', 'old_status', 'new_status', 'reason', 'changed_by', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
