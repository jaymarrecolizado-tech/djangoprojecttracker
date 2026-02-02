"""
App configuration for the projects app.
"""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Configuration for the projects app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    verbose_name = 'Projects'

    def ready(self):
        """Called when the app is ready."""
        pass
