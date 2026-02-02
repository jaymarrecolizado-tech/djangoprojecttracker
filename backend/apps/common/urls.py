"""
URL configuration for the common app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Health and monitoring endpoints
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('ready/', views.ReadinessCheckView.as_view(), name='readiness-check'),
    path('live/', views.LivenessCheckView.as_view(), name='liveness-check'),
    path('system/', views.SystemInfoView.as_view(), name='system-info'),
    path('api/status/', views.APIStatusView.as_view(), name='api-status'),
]
