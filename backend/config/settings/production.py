"""
Production settings for Project Tracking Management System.

This module contains settings specific to the production environment.
Security settings are strictly enforced.
"""

from .base import *
from .security import *  # Import security settings

# Validate environment on startup (optional, can be disabled after initial setup)
# from ..env_validator import validate_environment
# validate_environment('production')

# =============================================================================
# Debug Settings
# =============================================================================

DEBUG = False

# =============================================================================
# Allowed Hosts - Must be explicitly defined
# =============================================================================

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS must be set in production environment")

# =============================================================================
# Security Settings - Strict for production
# =============================================================================

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Additional Security Headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'  # Control referrer information

# =============================================================================
# Database Configuration
# =============================================================================

# Connection pooling for better performance
# CONN_MAX_AGE: persistent connections in seconds
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes

# Connection pooling settings (for mysqlclient)
DATABASES['default']['OPTIONS']['init_command'] += ";SET SESSION wait_timeout=600;SET SESSION interactive_timeout=600"

# Additional database optimizations
DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'
DATABASES['default']['OPTIONS']['sql_mode'] = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'

# =============================================================================
# CORS Settings - Restrictive for production
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# Only allow specific origins
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    ''
).split(',')

# =============================================================================
# Static Files - Whitenoise for production
# =============================================================================

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# =============================================================================
# Logging - Production level
# =============================================================================

LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'

# =============================================================================
# REST Framework - Production settings
# =============================================================================

# Remove browsable API renderer in production
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# =============================================================================
# Sentry Configuration (optional)
# =============================================================================

SENTRY_DSN = os.getenv('SENTRY_DSN', '')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

# =============================================================================
# Cache Settings - Production optimized
# =============================================================================

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'project_tracking'

# =============================================================================
# File Upload Settings - Production limits
# =============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB

# =============================================================================
# Celery Settings - Production
# =============================================================================

CELERY_TASK_ALWAYS_EAGER = False
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# =============================================================================
# Email Settings - Production
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@projecttracking.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'admin@projecttracking.com')

# Admin email for error notifications
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@projecttracking.com')),
]

MANAGERS = ADMINS
