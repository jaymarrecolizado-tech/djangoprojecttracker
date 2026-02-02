"""
Permission classes for the accounts app.

This module provides custom permission classes for role-based access control
in the Project Tracking Management System.
"""

from rest_framework import permissions
from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """
    Permission class that grants access only to admin users.

    Admin users include those with the 'admin' role and superusers.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is an admin.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if user is admin, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsManager(permissions.BasePermission):
    """
    Permission class that grants access to manager and admin users.

    Users with 'manager' or 'admin' roles can access resources
    protected by this permission.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is a manager or admin.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if user is manager or admin, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_manager
        )


class IsEditor(permissions.BasePermission):
    """
    Permission class that grants access to editor, manager, and admin users.

    Users with 'editor', 'manager', or 'admin' roles can access resources
    protected by this permission. This is typically used for write operations
    on projects.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is an editor or higher.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if user is editor or higher, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_editor
        )


class IsViewer(permissions.BasePermission):
    """
    Permission class that grants read access to all authenticated users.

    All authenticated users including viewers can access resources
    protected by this permission. This is the base permission level.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is authenticated.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if user is authenticated, False otherwise
        """
        return request.user and request.user.is_authenticated


class HasRolePermission(permissions.BasePermission):
    """
    Generic permission class that checks for a specific role or higher.

    Usage:
        permission_classes = [HasRolePermission]
        required_role = UserRole.EDITOR

    Attributes:
        required_role: The minimum role required for access
    """

    required_role = UserRole.VIEWER

    def has_permission(self, request, view) -> bool:
        """
        Check if the user has the required role or higher.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if user has required role, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role_permission(self.required_role)
        )


class ReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to all authenticated users.

    Safe methods (GET, HEAD, OPTIONS) are allowed for all authenticated users.
    Write methods require appropriate permissions from the view.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the request method is safe.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if method is safe and user is authenticated, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False

        return request.method in permissions.SAFE_METHODS


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows access to object owners or admins.

    Users can access objects they created, or admins can access any object.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Check if the user is the owner or an admin.

        Args:
            request: The incoming request
            view: The view being accessed
            obj: The object being accessed

        Returns:
            True if user is owner or admin, False otherwise
        """
        if request.user.is_admin:
            return True

        # Check if the object has a created_by attribute
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission class that allows users to access their own data or admins to access any data.

    This is useful for user profile endpoints where users should only
    access their own profile unless they are admins.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Check if the user is accessing their own data or is an admin.

        Args:
            request: The incoming request
            view: The view being accessed
            obj: The object being accessed (expected to be a User)

        Returns:
            True if user is self or admin, False otherwise
        """
        if request.user.is_admin:
            return True

        return obj == request.user


# Permission mapping for easy use
PERMISSION_CLASSES = {
    'admin': IsAdmin,
    'manager': IsManager,
    'editor': IsEditor,
    'viewer': IsViewer,
}


def get_permission_class(role: str):
    """
    Get the permission class for a given role.

    Args:
        role: The role name (admin, manager, editor, viewer)

    Returns:
        Permission class for the role, or IsViewer if not found
    """
    return PERMISSION_CLASSES.get(role.lower(), IsViewer)
