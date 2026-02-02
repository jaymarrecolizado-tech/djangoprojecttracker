"""
URL configuration for the monitoring app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='monitoring-dashboard'),
    
    # Metrics
    path('metrics/', views.MetricsView.as_view(), name='monitoring-metrics'),
    
    # Alerts
    path('alerts/', views.AlertsView.as_view(), name='monitoring-alerts'),
    path('alerts/<int:alert_id>/', views.AlertsView.as_view(), name='monitoring-alert-detail'),
    
    # Performance
    path('performance/', views.PerformanceView.as_view(), name='monitoring-performance'),
    
    # Events
    path('events/', views.EventsView.as_view(), name='monitoring-events'),
]
