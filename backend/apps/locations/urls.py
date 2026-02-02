"""
URL configuration for the locations app.

This module defines URL patterns for location management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProvinceViewSet,
    DistrictViewSet,
    MunicipalityViewSet,
    BarangayViewSet,
    LocationHierarchyView,
)

# Create a router for location ViewSets
router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'municipalities', MunicipalityViewSet, basename='municipality')
router.register(r'barangays', BarangayViewSet, basename='barangay')

# URL patterns
urlpatterns = [
    # Location hierarchy
    path('locations/hierarchy/', LocationHierarchyView.as_view(), name='location-hierarchy'),

    # Router URLs
    path('', include(router.urls)),
]
