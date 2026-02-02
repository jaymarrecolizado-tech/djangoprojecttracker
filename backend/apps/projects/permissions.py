"""
Permissions for the projects app.
"""

from rest_framework import permissions


class IsProjectEditor(permissions.BasePermission):
    """
    Permission class that grants access to project editors and above.
    """

    def has_permission(self, request, view) -> bool:
        """Check if user is an editor or above."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_editor
        )

    def has_object_permission(self, request, view, obj) -> bool:
        """Check object-level permissions."""
        if request.user.is_admin:
            return True
        return request.user.is_editor


class IsProjectOwnerOrEditor(permissions.BasePermission):
    """
    Permission class that grants access to project owners or editors.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if user is owner or editor."""
        if request.user.is_editor:
            return True
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False
