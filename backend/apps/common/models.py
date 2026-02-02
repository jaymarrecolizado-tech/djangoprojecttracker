"""
Base models for the Project Tracking Management System.

This module provides abstract base models that other models can inherit from
to get common fields and functionality.
"""

from django.db import models
from django.conf import settings


class TimestampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.

    This model adds created_at and updated_at fields to all inheriting models,
    automatically tracking when records are created and modified.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the record was last updated'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserTrackedModel(models.Model):
    """
    Abstract base model that provides user tracking fields.

    This model adds created_by and updated_by fields to track which users
    created and last modified the record.

    Attributes:
        created_by: User who created the record
        updated_by: User who last updated the record
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text='User who created this record'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text='User who last updated this record'
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.

    Instead of permanently deleting records, this model marks them as deleted
    by setting is_deleted to True. Deleted records can be restored if needed.

    Attributes:
        is_deleted: Flag indicating if the record is soft-deleted
        deleted_at: Timestamp when the record was soft-deleted
        deleted_by: User who soft-deleted the record
    """

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Flag indicating if the record is soft-deleted'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the record was soft-deleted'
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text='User who soft-deleted this record'
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, deleted_by=None):
        """
        Soft delete the instance instead of permanently deleting it.

        Args:
            using: Database alias to use
            keep_parents: Whether to keep parent models
            deleted_by: User who is performing the deletion
        """
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def restore(self, restored_by=None):
        """
        Restore a soft-deleted instance.

        Args:
            restored_by: User who is restoring the record
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the instance from the database.

        Args:
            using: Database alias to use
            keep_parents: Whether to keep parent models
        """
        super().delete(using=using, keep_parents=keep_parents)


class BaseModel(TimestampedModel, UserTrackedModel, SoftDeleteModel):
    """
    Comprehensive abstract base model combining all base functionalities.

    This model combines timestamp tracking, user tracking, and soft delete
    functionality into a single base class for maximum convenience.

    Inherits:
        TimestampedModel: created_at, updated_at fields
        UserTrackedModel: created_by, updated_by fields
        SoftDeleteModel: is_deleted, deleted_at, deleted_by fields
    """

    class Meta:
        abstract = True
        ordering = ['-created_at']


class NamedModel(models.Model):
    """
    Abstract base model for models that have a name field.

    Provides common name-related functionality like string representation
    and name-based ordering.

    Attributes:
        name: The name of the entity
    """

    name = models.CharField(
        max_length=255,
        help_text='Name of the entity'
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        """Return the string representation of the model."""
        return self.name


class CodeNamedModel(NamedModel):
    """
    Abstract base model for models that have both code and name fields.

    Useful for reference data that needs both a human-readable name
    and a machine-readable code.

    Attributes:
        code: Unique code for the entity
        name: Human-readable name of the entity
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique code for the entity'
    )

    class Meta:
        abstract = True
        ordering = ['code']

    def __str__(self):
        """Return the string representation of the model."""
        return f"{self.code} - {self.name}"
