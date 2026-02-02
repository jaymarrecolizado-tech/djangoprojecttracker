"""
Filters for the projects app.
"""

import django_filters
from django.db.models import Q

from .models import ProjectSite, ProjectType, ProjectStatus


class ProjectSiteFilter(django_filters.FilterSet):
    """FilterSet for ProjectSite model."""

    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.CharFilter(field_name='status')
    project_type = django_filters.NumberFilter(field_name='project_type')
    province = django_filters.NumberFilter(field_name='province')
    municipality = django_filters.NumberFilter(field_name='municipality')
    barangay = django_filters.NumberFilter(field_name='barangay')
    activation_date_after = django_filters.DateFilter(
        field_name='activation_date',
        lookup_expr='gte'
    )
    activation_date_before = django_filters.DateFilter(
        field_name='activation_date',
        lookup_expr='lte'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = ProjectSite
        fields = [
            'status', 'project_type',
            'province', 'municipality', 'barangay'
        ]

    def filter_search(self, queryset, name, value):
        """Filter by search term across multiple fields."""
        return queryset.filter(
            Q(site_code__icontains=value) |
            Q(site_name__icontains=value) |
            Q(remarks__icontains=value) |
            Q(project_type__name__icontains=value) |
            Q(province__name__icontains=value) |
            Q(municipality__name__icontains=value) |
            Q(barangay__name__icontains=value)
        )


class ProjectTypeFilter(django_filters.FilterSet):
    """FilterSet for ProjectType model."""

    is_active = django_filters.BooleanFilter(field_name='is_active')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = ProjectType
        fields = ['is_active']

    def filter_search(self, queryset, name, value):
        """Filter by search term."""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code_prefix__icontains=value) |
            Q(description__icontains=value)
        )
