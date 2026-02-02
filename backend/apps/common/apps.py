"""
App configuration for the common app.
"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration for the common app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    verbose_name = 'Common Utilities'

    def ready(self):
        """Called when the app is ready."""
        pass
