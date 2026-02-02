"""
Views for the accounts app.

This module provides API views for user authentication and management,
including login, logout, and user CRUD operations.
"""

from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.responses import (
    success_response,
    error_response,
    created_response,
    deleted_response,
    unauthorized_response,
)

from .models import User
from .permissions import IsManager, IsSelfOrAdmin
from .serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserPasswordChangeSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView:
    """
    API View for user login.

    Handles user authentication and session creation.

    POST /auth/login/
        Request: {"username": "user", "password": "pass"}
        Response: {"success": true, "data": {"user": {...}}}
    """

    @classmethod
    def as_view(cls):
        """Return the view function."""
        return csrf_protect(cls.post)

    @staticmethod
    def post(request: Request) -> Response:
        """
        Handle login POST request.

        Args:
            request: The incoming request with login credentials

        Returns:
            Response with user data on success, error on failure
        """
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return error_response(
                message='Login failed',
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data['user']
        login(request, user)

        return success_response(
            data={'user': CurrentUserSerializer(user).data},
            message='Login successful'
        )


class LogoutView:
    """
    API View for user logout.

    Handles session termination.

    POST /auth/logout/
        Response: {"success": true, "message": "Logout successful"}
    """

    @classmethod
    def as_view(cls):
        """Return the view function."""
        return cls.post

    @staticmethod
    def post(request: Request) -> Response:
        """
        Handle logout POST request.

        Args:
            request: The incoming request

        Returns:
            Response confirming logout
        """
        if not request.user.is_authenticated:
            return unauthorized_response('Not logged in')

        logout(request)
        return success_response(message='Logout successful')


class CurrentUserView:
    """
    API View for current user information.

    GET /auth/me/
        Response: {"success": true, "data": {"user": {...}}}
    """

    @classmethod
    def as_view(cls):
        """Return the view function."""
        return cls.get

    @staticmethod
    def get(request: Request) -> Response:
        """
        Handle GET request for current user.

        Args:
            request: The incoming request

        Returns:
            Response with current user data
        """
        if not request.user.is_authenticated:
            return unauthorized_response()

        return success_response(
            data={'user': CurrentUserSerializer(request.user).data}
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.

    Provides CRUD operations for user accounts.
    Requires manager or admin role for most operations.

    Endpoints:
        GET /users/ - List all users
        POST /users/ - Create new user
        GET /users/{id}/ - Get user details
        PUT /users/{id}/ - Update user
        PATCH /users/{id}/ - Partial update user
        DELETE /users/{id}/ - Delete user
        POST /users/{id}/change-password/ - Change user password
        POST /users/{id}/reset-password/ - Reset user password
    """

    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Get permission classes based on action.

        Returns:
            List of permission instances
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'change_password']:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Get serializer class based on action.

        Returns:
            Serializer class to use
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Get queryset based on user role.

        Regular users can only see themselves, managers/admins can see all.

        Returns:
            QuerySet of users
        """
        user = self.request.user
        if user.is_admin or user.is_manager:
            return self.queryset
        return self.queryset.filter(id=user.id)

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List all users.

        Args:
            request: The incoming request

        Returns:
            Response with list of users
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'users': serializer.data})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Get a specific user.

        Args:
            request: The incoming request

        Returns:
            Response with user data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'user': serializer.data})

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new user.

        Args:
            request: The incoming request with user data

        Returns:
            Response with created user data
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Failed to create user',
                errors=serializer.errors
            )

        user = serializer.save()
        return created_response(
            data=UserSerializer(user).data,
            message='User created successfully'
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a user.

        Args:
            request: The incoming request with updated data

        Returns:
            Response with updated user data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        if not serializer.is_valid():
            return error_response(
                message='Failed to update user',
                errors=serializer.errors
            )

        user = serializer.save()
        return success_response(
            data={'user': UserSerializer(user).data},
            message='User updated successfully'
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Delete (deactivate) a user.

        Args:
            request: The incoming request

        Returns:
            Response confirming deletion
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return deleted_response('User deactivated successfully')

    @action(detail=True, methods=['post'])
    def change_password(self, request: Request, pk=None) -> Response:
        """
        Change user's password.

        Args:
            request: The incoming request with password data
            pk: User ID

        Returns:
            Response confirming password change
        """
        user = self.get_object()
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return error_response(
                message='Failed to change password',
                errors=serializer.errors
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return success_response(message='Password changed successfully')

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def reset_password(self, request: Request, pk=None) -> Response:
        """
        Reset user's password (manager/admin only).

        Args:
            request: The incoming request
            pk: User ID

        Returns:
            Response with new temporary password
        """
        import secrets
        import string

        user = self.get_object()

        # Generate a secure temporary password
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user.set_password(temp_password)
        user.save()

        return success_response(
            data={'temporary_password': temp_password},
            message='Password reset successfully. User must change password on next login.'
        )

    @action(detail=False, methods=['get'])
    def roles(self, request: Request) -> Response:
        """
        Get list of available user roles.

        Args:
            request: The incoming request

        Returns:
            Response with role options
        """
        from .models import UserRole

        roles = [
            {'value': role.value, 'label': role.label}
            for role in UserRole
        ]
        return success_response(data={'roles': roles})
