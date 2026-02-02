"""
Development settings for Project Tracking Management System.

This module contains settings specific to the development environment.
"""

from .base import *

# =============================================================================
# Debug Settings
# =============================================================================

DEBUG = True

# =============================================================================
# Allowed Hosts
# =============================================================================

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# =============================================================================
# Database Configuration
# =============================================================================

# Use the same database configuration from base.py for development
# Override if needed for local development

# =============================================================================
# CORS Settings - More permissive for development
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# Email Backend - Console for development
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# Debug Toolbar (optional)
# =============================================================================

# INSTALLED_APPS.insert(0, 'debug_toolbar')
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']

# =============================================================================
# Logging - More verbose in development
# =============================================================================

LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# =============================================================================
# REST Framework - Additional renderers for development
# =============================================================================

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
    'rest_framework.renderers.BrowsableAPIRenderer'
)

# =============================================================================
# Security Settings - Relaxed for development
# =============================================================================

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# =============================================================================
# Static Files - Serve from development server
# =============================================================================

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
