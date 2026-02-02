"""
Serializers for the locations app.

This module provides serializers for location models,
including Province, District, Municipality, and Barangay.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Province, District, Municipality, Barangay


class ProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for Province model.

    Provides province information with computed counts.
    """

    district_count = serializers.IntegerField(read_only=True)
    municipality_count = serializers.IntegerField(read_only=True)
    barangay_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta options for ProvinceSerializer."""
        model = Province
        fields = [
            'id', 'name', 'code',
            'district_count', 'municipality_count', 'barangay_count'
        ]


class ProvinceDetailSerializer(ProvinceSerializer):
    """
    Detailed serializer for Province model.

    Includes centroid and boundary GeoJSON representation.
    """

    centroid = serializers.SerializerMethodField()
    boundary = serializers.SerializerMethodField()

    class Meta(ProvinceSerializer.Meta):
        fields = ProvinceSerializer.Meta.fields + ['centroid', 'boundary']

    def get_centroid(self, obj: Province) -> dict:
        """Get centroid as GeoJSON."""
        if obj.centroid:
            return {
                'type': 'Point',
                'coordinates': [obj.centroid.x, obj.centroid.y]
            }
        return None

    def get_boundary(self, obj: Province) -> dict:
        """Get boundary as GeoJSON."""
        if obj.boundary:
            return {
                'type': 'Polygon',
                'coordinates': obj.boundary.coords
            }
        return None


class DistrictSerializer(serializers.ModelSerializer):
    """
    Serializer for District model.

    Provides district information with parent province details.
    """

    province = ProvinceSerializer(read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(),
        source='province',
        write_only=True
    )
    municipality_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta options for DistrictSerializer."""
        model = District
        fields = [
            'id', 'name', 'code',
            'province', 'province_id',
            'municipality_count'
        ]


class DistrictDetailSerializer(DistrictSerializer):
    """
    Detailed serializer for District model.

    Includes centroid and boundary GeoJSON representation.
    """

    centroid = serializers.SerializerMethodField()
    boundary = serializers.SerializerMethodField()

    class Meta(DistrictSerializer.Meta):
        fields = DistrictSerializer.Meta.fields + ['centroid', 'boundary']

    def get_centroid(self, obj: District) -> dict:
        """Get centroid as GeoJSON."""
        if obj.centroid:
            return {
                'type': 'Point',
                'coordinates': [obj.centroid.x, obj.centroid.y]
            }
        return None

    def get_boundary(self, obj: District) -> dict:
        """Get boundary as GeoJSON."""
        if obj.boundary:
            return {
                'type': 'Polygon',
                'coordinates': obj.boundary.coords
            }
        return None


class MunicipalityListSerializer(serializers.ModelSerializer):
    """
    List serializer for Municipality model.

    Provides basic municipality information.
    """

    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        """Meta options for MunicipalityListSerializer."""
        model = Municipality
        fields = [
            'id', 'name', 'code', 'is_city', 'city_class',
            'province_name'
        ]


class MunicipalitySerializer(serializers.ModelSerializer):
    """
    Serializer for Municipality model.

    Provides municipality information with parent location details.
    """

    province = ProvinceSerializer(read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(),
        source='province',
        write_only=True
    )
    district = DistrictSerializer(read_only=True)
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        source='district',
        write_only=True,
        required=False,
        allow_null=True
    )
    barangay_count = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        """Meta options for MunicipalitySerializer."""
        model = Municipality
        fields = [
            'id', 'name', 'code', 'is_city', 'city_class', 'full_name',
            'province', 'province_id',
            'district', 'district_id',
            'barangay_count'
        ]


class MunicipalityDetailSerializer(MunicipalitySerializer):
    """
    Detailed serializer for Municipality model.

    Includes centroid and boundary GeoJSON representation.
    """

    centroid = serializers.SerializerMethodField()
    boundary = serializers.SerializerMethodField()

    class Meta(MunicipalitySerializer.Meta):
        fields = MunicipalitySerializer.Meta.fields + ['centroid', 'boundary']

    def get_centroid(self, obj: Municipality) -> dict:
        """Get centroid as GeoJSON."""
        if obj.centroid:
            return {
                'type': 'Point',
                'coordinates': [obj.centroid.x, obj.centroid.y]
            }
        return None

    def get_boundary(self, obj: Municipality) -> dict:
        """Get boundary as GeoJSON."""
        if obj.boundary:
            return {
                'type': 'Polygon',
                'coordinates': obj.boundary.coords
            }
        return None


class BarangayListSerializer(serializers.ModelSerializer):
    """
    List serializer for Barangay model.

    Provides basic barangay information.
    """

    municipality_name = serializers.CharField(source='municipality.name', read_only=True)
    province_name = serializers.CharField(source='municipality.province.name', read_only=True)

    class Meta:
        """Meta options for BarangayListSerializer."""
        model = Barangay
        fields = [
            'id', 'name', 'code', 'urban_rural',
            'municipality_name', 'province_name'
        ]


class BarangaySerializer(serializers.ModelSerializer):
    """
    Serializer for Barangay model.

    Provides barangay information with parent municipality details.
    """

    municipality = MunicipalityListSerializer(read_only=True)
    municipality_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(),
        source='municipality',
        write_only=True
    )
    full_address = serializers.CharField(read_only=True)

    class Meta:
        """Meta options for BarangaySerializer."""
        model = Barangay
        fields = [
            'id', 'name', 'code', 'urban_rural', 'full_address',
            'municipality', 'municipality_id'
        ]


class BarangayDetailSerializer(BarangaySerializer):
    """
    Detailed serializer for Barangay model.

    Includes centroid and boundary GeoJSON representation.
    """

    centroid = serializers.SerializerMethodField()
    boundary = serializers.SerializerMethodField()

    class Meta(BarangaySerializer.Meta):
        fields = BarangaySerializer.Meta.fields + ['centroid', 'boundary']

    def get_centroid(self, obj: Barangay) -> dict:
        """Get centroid as GeoJSON."""
        if obj.centroid:
            return {
                'type': 'Point',
                'coordinates': [obj.centroid.x, obj.centroid.y]
            }
        return None

    def get_boundary(self, obj: Barangay) -> dict:
        """Get boundary as GeoJSON."""
        if obj.boundary:
            return {
                'type': 'Polygon',
                'coordinates': obj.boundary.coords
            }
        return None


class LocationHierarchySerializer(serializers.Serializer):
    """
    Serializer for location hierarchy.

    Provides a complete hierarchy from province to barangay.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    children = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
