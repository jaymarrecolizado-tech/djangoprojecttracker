"""
Django app configuration for the monitoring app.
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """Configuration for the monitoring application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'Monitoring'
    
    def ready(self):
        """Called when the app is ready."""
        # Import signal handlers
        pass
