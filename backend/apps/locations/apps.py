"""
App configuration for the locations app.
"""

from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """Configuration for the locations app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.locations'
    verbose_name = 'Locations'

    def ready(self):
        """Called when the app is ready."""
        pass
