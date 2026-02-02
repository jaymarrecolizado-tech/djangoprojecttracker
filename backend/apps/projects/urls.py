"""
URL configuration for the projects app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectSiteViewSet, ProjectTypeViewSet

router = DefaultRouter()
router.register(r'project-types', ProjectTypeViewSet, basename='project-type')
router.register(r'projects', ProjectSiteViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
