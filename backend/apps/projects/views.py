"""
Views for the projects app.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from apps.common.pagination import StandardResultsSetPagination
from apps.common.responses import success_response, error_response, created_response, deleted_response
from apps.accounts.permissions import IsEditor, IsAdmin

from .models import ProjectSite, ProjectType, ProjectStatusHistory, ProjectStatus
from .serializers import (
    ProjectSiteSerializer,
    ProjectSiteListSerializer,
    ProjectSiteCreateSerializer,
    ProjectSiteUpdateSerializer,
    ProjectSiteDetailSerializer,
    ProjectTypeSerializer,
    ProjectStatusHistorySerializer,
    ProjectStatusUpdateSerializer
)
from .filters import ProjectSiteFilter, ProjectTypeFilter
from .permissions import IsProjectEditor


class ProjectTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectType model."""

    queryset = ProjectType.objects.annotate(
        project_count=Count('projects', filter=Q(projects__is_deleted=False))
    ).order_by('name')
    serializer_class = ProjectTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProjectTypeFilter
    search_fields = ['name', 'code_prefix']

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """List all project types."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'project_types': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """Get a specific project type."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'project_type': serializer.data})

    def create(self, request, *args, **kwargs):
        """Create a new project type."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message='Validation failed', errors=serializer.errors)
        project_type = serializer.save()
        return created_response(data={'project_type': ProjectTypeSerializer(project_type).data})


class ProjectSiteViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectSite model."""

    queryset = ProjectSite.objects.filter(is_deleted=False).select_related(
        'project_type', 'barangay', 'municipality', 'province',
        'created_by', 'updated_by'
    ).order_by('-created_at')
    serializer_class = ProjectSiteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectSiteFilter
    search_fields = ['site_code', 'site_name', 'remarks']
    ordering_fields = ['created_at', 'activation_date', 'site_name', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Get serializer class based on action."""
        if self.action == 'list':
            return ProjectSiteListSerializer
        if self.action == 'retrieve':
            return ProjectSiteDetailSerializer
        if self.action == 'create':
            return ProjectSiteCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjectSiteUpdateSerializer
        return ProjectSiteSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_status']:
            return [IsProjectEditor()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """List all project sites."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'projects': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """Get a specific project site."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'project': serializer.data})

    def create(self, request, *args, **kwargs):
        """Create a new project site."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message='Validation failed', errors=serializer.errors)
        project = serializer.save(created_by=request.user)
        return created_response(
            data={'project': ProjectSiteSerializer(project).data},
            message='Project created successfully'
        )

    def update(self, request, *args, **kwargs):
        """Update a project site."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return error_response(message='Validation failed', errors=serializer.errors)
        project = serializer.save(updated_by=request.user)
        return success_response(
            data={'project': ProjectSiteSerializer(project).data},
            message='Project updated successfully'
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete a project site."""
        instance = self.get_object()
        instance.delete(deleted_by=request.user)
        return deleted_response('Project deleted successfully')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update project status with history tracking."""
        project = self.get_object()
        serializer = ProjectStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message='Validation failed', errors=serializer.errors)

        old_status = project.status
        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        if old_status == new_status:
            return error_response(message='New status must be different from current status')

        # Update project status
        project.status = new_status
        project.updated_by = request.user
        project.save()

        # Create status history
        ProjectStatusHistory.objects.create(
            project=project,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by=request.user
        )

        return success_response(
            data={'project': ProjectSiteSerializer(project).data},
            message='Status updated successfully'
        )

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get project status history."""
        project = self.get_object()
        history = project.status_history.all()
        serializer = ProjectStatusHistorySerializer(history, many=True)
        return success_response(data={'history': serializer.data})

    @action(detail=False, methods=['get'])
    def status_options(self, request):
        """Get project status options."""
        statuses = [
            {'value': status.value, 'label': status.label, 'color': self._get_status_color(status.value)}
            for status in ProjectStatus
        ]
        return success_response(data={'statuses': statuses})

    def _get_status_color(self, status):
        """Get color for status."""
        colors = {
            'pending': '#F59E0B',
            'in_progress': '#3B82F6',
            'done': '#10B981',
            'cancelled': '#EF4444',
            'on_hold': '#6B7280',
        }
        return colors.get(status, '#6B7280')
