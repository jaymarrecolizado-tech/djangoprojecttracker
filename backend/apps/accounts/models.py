"""
Custom User model for the Project Tracking Management System.

This module provides a custom User model with role-based access control,
extending Django's AbstractUser with additional fields for the system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """
    User role choices for role-based access control.

    Attributes:
        ADMIN: Full system access
        MANAGER: Can manage users and projects
        EDITOR: Can create and edit projects
        VIEWER: Read-only access
    """
    ADMIN = 'admin', _('Admin')
    MANAGER = 'manager', _('Manager')
    EDITOR = 'editor', _('Editor')
    VIEWER = 'viewer', _('Viewer')


class User(AbstractUser):
    """
    Custom User model with role-based access control.

    Extends Django's AbstractUser with additional fields for the
    Project Tracking Management System, including full name and role.

    Attributes:
        full_name: User's full name
        role: User's role for access control
        is_active: Whether the user account is active
        email: User's email address (unique)

    Example:
        >>> user = User.objects.create_user(
        ...     username='john_doe',
        ...     email='john@example.com',
        ...     full_name='John Doe',
        ...     role=UserRole.EDITOR,
        ...     password='securepassword123'
        ... )
    """

    full_name = models.CharField(
        max_length=100,
        help_text=_('User\'s full name')
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
        help_text=_('User role for access control')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the user account is active')
    )
    email = models.EmailField(
        unique=True,
        help_text=_('User\'s email address')
    )

    # Override the USERNAME_FIELD to use email for authentication
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        """Meta options for the User model."""
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        db_table = 'auth_user'

    def __str__(self) -> str:
        """Return string representation of the user."""
        return f"{self.full_name} ({self.username})"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_manager(self) -> bool:
        """Check if user has manager role or higher."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER] or self.is_superuser

    @property
    def is_editor(self) -> bool:
        """Check if user has editor role or higher."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.EDITOR] or self.is_superuser

    @property
    def is_viewer(self) -> bool:
        """Check if user has viewer role or higher (all authenticated users)."""
        return self.is_authenticated

    def get_role_display_name(self) -> str:
        """Get the human-readable role name."""
        return self.get_role_display()

    def has_role_permission(self, required_role: str) -> bool:
        """
        Check if user has the required role or higher.

        Args:
            required_role: The minimum required role

        Returns:
            True if user has required role, False otherwise
        """
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.EDITOR: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4,
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 5)

        return user_level >= required_level or self.is_superuser
