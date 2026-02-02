"""
Admin configuration for the accounts app.

This module customizes the Django admin interface for User management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom UserAdmin for managing users in the Django admin interface.

    Provides enhanced display and filtering capabilities for the User model.
    """

    # Display settings
    list_display = [
        'username',
        'email',
        'full_name',
        'role',
        'is_active',
        'is_staff',
        'date_joined',
    ]

    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    ]

    search_fields = [
        'username',
        'email',
        'full_name',
    ]

    ordering = ['-date_joined']

    # Field organization
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'full_name',
                    'role',
                    'password1',
                    'password2',
                ),
            }
        ),
    )

    readonly_fields = ['last_login', 'date_joined']

    # Actions
    actions = ['make_active', 'make_inactive', 'set_role_admin', 'set_role_manager', 'set_role_editor', 'set_role_viewer']

    @admin.action(description=_('Activate selected users'))
    def make_active(self, request, queryset):
        """Activate selected users."""
        queryset.update(is_active=True)

    @admin.action(description=_('Deactivate selected users'))
    def make_inactive(self, request, queryset):
        """Deactivate selected users."""
        queryset.update(is_active=False)

    @admin.action(description=_('Set role to Admin'))
    def set_role_admin(self, request, queryset):
        """Set selected users' role to Admin."""
        queryset.update(role=UserRole.ADMIN)

    @admin.action(description=_('Set role to Manager'))
    def set_role_manager(self, request, queryset):
        """Set selected users' role to Manager."""
        queryset.update(role=UserRole.MANAGER)

    @admin.action(description=_('Set role to Editor'))
    def set_role_editor(self, request, queryset):
        """Set selected users' role to Editor."""
        queryset.update(role=UserRole.EDITOR)

    @admin.action(description=_('Set role to Viewer'))
    def set_role_viewer(self, request, queryset):
        """Set selected users' role to Viewer."""
        queryset.update(role=UserRole.VIEWER)

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form based on user permissions.

        Non-superusers cannot assign superuser status or change certain fields.
        """
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Restrict fields for non-superusers
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True
        return form

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of users through admin.

        Users should be deactivated instead.
        """
        return False
