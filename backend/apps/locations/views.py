"""
Views for the locations app.

This module provides API views for location management,
including Province, District, Municipality, and Barangay.
"""

from django.db.models import Count, Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.pagination import StandardResultsSetPagination, SmallResultsSetPagination
from apps.common.responses import success_response

from .models import Province, District, Municipality, Barangay
from .serializers import (
    ProvinceSerializer,
    ProvinceDetailSerializer,
    DistrictSerializer,
    DistrictDetailSerializer,
    MunicipalitySerializer,
    MunicipalityListSerializer,
    MunicipalityDetailSerializer,
    BarangaySerializer,
    BarangayListSerializer,
    BarangayDetailSerializer,
)


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Province model.

    Provides read-only access to province data.

    Endpoints:
        GET /provinces/ - List all provinces
        GET /provinces/{id}/ - Get province details
        GET /provinces/{id}/municipalities/ - Get municipalities in province
    """

    queryset = Province.objects.annotate(
        district_count=Count('districts', distinct=True),
        municipality_count=Count('municipalities', distinct=True),
        barangay_count=Count('municipalities__barangays', distinct=True)
    ).order_by('name')
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SmallResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    lookup_field = 'pk'

    def get_serializer_class(self):
        """Get serializer class based on action."""
        if self.action == 'retrieve':
            return ProvinceDetailSerializer
        return ProvinceSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all provinces."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'provinces': serializer.data})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get a specific province."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'province': serializer.data})

    @action(detail=True, methods=['get'])
    def municipalities(self, request: Request, pk=None) -> Response:
        """Get municipalities in a province."""
        province = self.get_object()
        municipalities = Municipality.objects.filter(
            province=province
        ).annotate(
            barangay_count=Count('barangays')
        ).order_by('name')

        serializer = MunicipalityListSerializer(municipalities, many=True)
        return success_response(data={'municipalities': serializer.data})

    @action(detail=True, methods=['get'])
    def districts(self, request: Request, pk=None) -> Response:
        """Get districts in a province."""
        province = self.get_object()
        districts = District.objects.filter(
            province=province
        ).annotate(
            municipality_count=Count('municipalities')
        ).order_by('name')

        serializer = DistrictSerializer(districts, many=True)
        return success_response(data={'districts': serializer.data})


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for District model.

    Provides read-only access to district data.

    Endpoints:
        GET /districts/ - List all districts
        GET /districts/{id}/ - Get district details
    """

    queryset = District.objects.annotate(
        municipality_count=Count('municipalities')
    ).select_related('province').order_by('province__name', 'name')
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SmallResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['province']
    search_fields = ['name', 'code']

    def get_serializer_class(self):
        """Get serializer class based on action."""
        if self.action == 'retrieve':
            return DistrictDetailSerializer
        return DistrictSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all districts."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'districts': serializer.data})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get a specific district."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'district': serializer.data})


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Municipality model.

    Provides read-only access to municipality data.

    Endpoints:
        GET /municipalities/ - List all municipalities
        GET /municipalities/{id}/ - Get municipality details
        GET /municipalities/{id}/barangays/ - Get barangays in municipality
    """

    queryset = Municipality.objects.annotate(
        barangay_count=Count('barangays')
    ).select_related('province', 'district').order_by('province__name', 'name')
    serializer_class = MunicipalitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['province', 'district', 'is_city']
    search_fields = ['name', 'code']

    def get_serializer_class(self):
        """Get serializer class based on action."""
        if self.action == 'retrieve':
            return MunicipalityDetailSerializer
        return MunicipalitySerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all municipalities."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'municipalities': serializer.data})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get a specific municipality."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'municipality': serializer.data})

    @action(detail=True, methods=['get'])
    def barangays(self, request: Request, pk=None) -> Response:
        """Get barangays in a municipality."""
        municipality = self.get_object()
        barangays = Barangay.objects.filter(
            municipality=municipality
        ).order_by('name')

        serializer = BarangayListSerializer(barangays, many=True)
        return success_response(data={'barangays': serializer.data})


class BarangayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Barangay model.

    Provides read-only access to barangay data.

    Endpoints:
        GET /barangays/ - List all barangays
        GET /barangays/{id}/ - Get barangay details
    """

    queryset = Barangay.objects.select_related(
        'municipality', 'municipality__province'
    ).order_by('municipality__province__name', 'municipality__name', 'name')
    serializer_class = BarangaySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['municipality', 'municipality__province', 'urban_rural']
    search_fields = ['name', 'code']

    def get_serializer_class(self):
        """Get serializer class based on action."""
        if self.action == 'retrieve':
            return BarangayDetailSerializer
        return BarangaySerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all barangays."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'barangays': serializer.data})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get a specific barangay."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data={'barangay': serializer.data})

    @action(detail=False, methods=['get'])
    def search(self, request: Request) -> Response:
        """Search barangays by name."""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return success_response(
                data={'barangays': []},
                message='Please provide at least 2 characters for search'
            )

        barangays = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(municipality__name__icontains=query) |
            Q(municipality__province__name__icontains=query)
        )[:20]  # Limit to 20 results

        serializer = BarangayListSerializer(barangays, many=True)
        return success_response(data={'barangays': serializer.data})


class LocationHierarchyView:
    """
    API View for location hierarchy.

    Provides hierarchical data of all locations.

    GET /locations/hierarchy/
        Response: {"success": true, "data": {"provinces": [...]}}
    """

    @classmethod
    def as_view(cls):
        """Return the view function."""
        return cls.get

    @staticmethod
    def get(request: Request) -> Response:
        """
        Get the complete location hierarchy.

        Args:
            request: The incoming request

        Returns:
            Response with hierarchical location data
        """
        provinces = Province.objects.prefetch_related(
            'municipalities',
            'municipalities__barangays'
        ).order_by('name')

        data = []
        for province in provinces:
            province_data = {
                'id': province.id,
                'name': province.name,
                'code': province.code,
                'type': 'province',
                'municipalities': []
            }

            for municipality in province.municipalities.all():
                municipality_data = {
                    'id': municipality.id,
                    'name': municipality.name,
                    'code': municipality.code,
                    'type': 'city' if municipality.is_city else 'municipality',
                    'is_city': municipality.is_city,
                    'barangays': []
                }

                for barangay in municipality.barangays.all():
                    municipality_data['barangays'].append({
                        'id': barangay.id,
                        'name': barangay.name,
                        'code': barangay.code,
                        'type': 'barangay',
                        'urban_rural': barangay.urban_rural
                    })

                province_data['municipalities'].append(municipality_data)

            data.append(province_data)

        return success_response(data={'provinces': data})
