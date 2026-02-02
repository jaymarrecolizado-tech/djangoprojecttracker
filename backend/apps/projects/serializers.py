"""
Serializers for the projects app.
"""

from rest_framework import serializers
from django.contrib.gis.geos import Point

from apps.locations.serializers import (
    BarangayListSerializer,
    MunicipalityListSerializer,
    ProvinceSerializer
)
from apps.accounts.serializers import UserSerializer

from .models import ProjectType, ProjectSite, ProjectStatusHistory, ProjectStatus


class ProjectTypeSerializer(serializers.ModelSerializer):
    """Serializer for ProjectType model."""

    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProjectType
        fields = ['id', 'name', 'code_prefix', 'color_code', 'description', 'is_active', 'project_count']


class ProjectStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for ProjectStatusHistory model."""

    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)

    class Meta:
        model = ProjectStatusHistory
        fields = [
            'id', 'old_status', 'old_status_display',
            'new_status', 'new_status_display',
            'reason', 'changed_by_name', 'created_at'
        ]


class ProjectSiteListSerializer(serializers.ModelSerializer):
    """List serializer for ProjectSite model."""

    project_type_name = serializers.CharField(source='project_type.name', read_only=True)
    project_type_color = serializers.CharField(source='project_type.color_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)
    municipality_name = serializers.CharField(source='municipality.name', read_only=True)
    barangay_name = serializers.CharField(source='barangay.name', read_only=True)

    class Meta:
        model = ProjectSite
        fields = [
            'id', 'site_code', 'site_name',
            'project_type_name', 'project_type_color',
            'status', 'status_display', 'status_color',
            'province_name', 'municipality_name', 'barangay_name',
            'latitude', 'longitude',
            'activation_date', 'created_at'
        ]


class ProjectSiteSerializer(serializers.ModelSerializer):
    """Serializer for ProjectSite model."""

    project_type = ProjectTypeSerializer(read_only=True)
    project_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProjectType.objects.filter(is_active=True),
        source='project_type',
        write_only=True
    )
    barangay = BarangayListSerializer(read_only=True)
    barangay_id = serializers.PrimaryKeyRelatedField(
        queryset='locations.Barangay'.objects.all(),
        source='barangay',
        write_only=True
    )
    municipality = MunicipalityListSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(read_only=True)
    location_address = serializers.CharField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)

    class Meta:
        model = ProjectSite
        fields = [
            'id', 'site_code', 'site_name',
            'project_type', 'project_type_id',
            'barangay', 'barangay_id',
            'municipality', 'province',
            'latitude', 'longitude', 'location',
            'activation_date',
            'status', 'status_display', 'status_color',
            'remarks', 'metadata',
            'location_address',
            'created_by_name', 'updated_by_name',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'location', 'is_deleted']

    def validate(self, attrs):
        """Validate the data."""
        # Ensure barangay's municipality and province match
        barangay = attrs.get('barangay')
        if barangay:
            attrs['municipality'] = barangay.municipality
            attrs['province'] = barangay.municipality.province
        return attrs


class ProjectSiteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ProjectSite."""

    project_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProjectType.objects.filter(is_active=True),
        source='project_type'
    )
    barangay_id = serializers.PrimaryKeyRelatedField(
        queryset='locations.Barangay'.objects.all(),
        source='barangay'
    )

    class Meta:
        model = ProjectSite
        fields = [
            'site_code', 'site_name',
            'project_type_id', 'barangay_id',
            'latitude', 'longitude',
            'activation_date', 'status', 'remarks', 'metadata'
        ]

    def validate_site_code(self, value):
        """Validate site code uniqueness."""
        if ProjectSite.objects.filter(site_code=value, is_deleted=False).exists():
            raise serializers.ValidationError('Site code already exists.')
        return value


class ProjectSiteUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ProjectSite."""

    project_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProjectType.objects.filter(is_active=True),
        source='project_type',
        required=False
    )
    barangay_id = serializers.PrimaryKeyRelatedField(
        queryset='locations.Barangay'.objects.all(),
        source='barangay',
        required=False
    )

    class Meta:
        model = ProjectSite
        fields = [
            'site_name', 'project_type_id', 'barangay_id',
            'latitude', 'longitude',
            'activation_date', 'status', 'remarks', 'metadata'
        ]

    def validate(self, attrs):
        """Validate the data."""
        # Ensure barangay's municipality and province match
        barangay = attrs.get('barangay')
        if barangay:
            attrs['municipality'] = barangay.municipality
            attrs['province'] = barangay.municipality.province
        return attrs


class ProjectSiteDetailSerializer(ProjectSiteSerializer):
    """Detailed serializer for ProjectSite model."""

    status_history = ProjectStatusHistorySerializer(many=True, read_only=True)

    class Meta(ProjectSiteSerializer.Meta):
        fields = ProjectSiteSerializer.Meta.fields + ['status_history']


class ProjectStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating project status."""

    status = serializers.ChoiceField(choices=ProjectStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
