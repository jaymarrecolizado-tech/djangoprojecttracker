"""URLs for import_export app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportViewSet, ExportViewSet

router = DefaultRouter()
router.register(r'imports', ImportViewSet, basename='import')
router.register(r'exports', ExportViewSet, basename='export')

urlpatterns = [
    path('', include(router.urls)),
]
