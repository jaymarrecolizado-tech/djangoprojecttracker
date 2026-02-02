"""
Root URL configuration for Project Tracking Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API version prefix
API_PREFIX = f'api/{settings.API_VERSION}'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Schema Documentation
    path(f'{API_PREFIX}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_PREFIX}/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_PREFIX}/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # App URLs
    path(f'{API_PREFIX}/auth/', include('apps.accounts.urls')),
    # path(f'{API_PREFIX}/', include('apps.locations.urls')),  # Temporarily commented - requires GDAL
    # path(f'{API_PREFIX}/', include('apps.projects.urls')),  # Temporarily commented - requires GDAL
    # path(f'{API_PREFIX}/geo/', include('apps.geo.urls')),  # Temporarily commented - requires GDAL
    # path(f'{API_PREFIX}/import/', include('apps.import_export.urls')),  # Temporarily commented - may depend on projects
    # path(f'{API_PREFIX}/reports/', include('apps.reports.urls')),  # Temporarily commented - may depend on projects
    path(f'{API_PREFIX}/audit/', include('apps.audit.urls')),
    # path(f'{API_PREFIX}/notifications/', include('apps.notifications.urls')),  # Temporarily commented - imports projects models
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
