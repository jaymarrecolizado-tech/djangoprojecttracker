"""URLs for geo app."""
from django.urls import path
from .views import MapDataView, NearbyProjectsView, BoundsFilterView

urlpatterns = [
    path('map-data/', MapDataView.as_view(), name='map-data'),
    path('nearby/', NearbyProjectsView.as_view(), name='nearby-projects'),
    path('bounds/', BoundsFilterView.as_view(), name='bounds-filter'),
]
