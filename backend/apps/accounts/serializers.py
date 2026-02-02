"""
Serializers for the accounts app.

This module provides serializers for user authentication and management,
including user serialization, login, and registration.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Provides full user information including role and status.
    Used for retrieving user details and user management.

    Example:
        >>> serializer = UserSerializer(user)
        >>> serializer.data
        {
            'id': 1,
            'username': 'john_doe',
            'email': 'john@example.com',
            'full_name': 'John Doe',
            'role': 'editor',
            'is_active': True,
            'date_joined': '2024-01-01T00:00:00Z'
        }
    """

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_manager = serializers.BooleanField(read_only=True)
    is_editor = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta options for UserSerializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'role_display',
            'is_active', 'is_admin', 'is_manager', 'is_editor',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.

    Includes password validation and confirmation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        """Meta options for UserCreateSerializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'password', 'password_confirm', 'is_active'
        ]
        read_only_fields = ['id']

    def validate(self, attrs: dict) -> dict:
        """
        Validate that passwords match.

        Args:
            attrs: Dictionary of field values

        Returns:
            Validated attributes

        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError({'password_confirm': 'Passwords do not match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        """
        Create a new user with encrypted password.

        Args:
            validated_data: Validated serializer data

        Returns:
            Created User instance
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.

    Allows updating user information without requiring password.
    """

    class Meta:
        """Meta options for UserUpdateSerializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'is_active'
        ]
        read_only_fields = ['id']


class UserPasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.

    Requires old password for verification and validates new password.
    """

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate password change data.

        Args:
            attrs: Dictionary of field values

        Returns:
            Validated attributes

        Raises:
            ValidationError: If passwords don't match or old password is incorrect
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise ValidationError({'new_password_confirm': 'Passwords do not match'})
        return attrs

    def validate_old_password(self, value: str) -> str:
        """
        Validate that the old password is correct.

        Args:
            value: Old password to validate

        Returns:
            Validated password

        Raises:
            ValidationError: If old password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('Old password is incorrect')
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates username and password credentials.

    Example:
        >>> serializer = LoginSerializer(data={
        ...     'username': 'john_doe',
        ...     'password': 'securepassword123'
        ... })
        >>> if serializer.is_valid():
        ...     user = serializer.validated_data['user']
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate login credentials.

        Args:
            attrs: Dictionary containing username and password

        Returns:
            Validated data with user object

        Raises:
            ValidationError: If credentials are invalid
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )

            if not user:
                raise ValidationError('Invalid username or password')

            if not user.is_active:
                raise ValidationError('User account is disabled')

            attrs['user'] = user
        else:
            raise ValidationError('Must provide both username and password')

        return attrs


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the currently authenticated user.

    Provides comprehensive information about the logged-in user,
    including permissions.
    """

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        """Meta options for CurrentUserSerializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'role_display',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'permissions'
        ]

    def get_permissions(self, obj: User) -> dict:
        """
        Get user's permission flags.

        Args:
            obj: User instance

        Returns:
            Dictionary of permission flags
        """
        return {
            'is_admin': obj.is_admin,
            'is_manager': obj.is_manager,
            'is_editor': obj.is_editor,
            'can_create_projects': obj.is_editor,
            'can_edit_projects': obj.is_editor,
            'can_delete_projects': obj.is_editor,
            'can_manage_users': obj.is_manager,
            'can_view_audit_logs': obj.is_admin,
            'can_import_csv': obj.is_editor,
            'can_export_data': obj.is_viewer,
        }
