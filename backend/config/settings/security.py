"""
Security settings and middleware configuration for Project Tracking Management System.

This module contains security-related settings including:
- Content Security Policy (CSP) configuration
- Security headers middleware
- Rate limiting configuration
- Password validation rules
"""

import os

# =============================================================================
# Content Security Policy (CSP) Settings
# =============================================================================
# CSP helps prevent XSS attacks by controlling which resources can be loaded

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Required for some React features
    "'unsafe-eval'",    # Required for React development
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Required for styled-components and inline styles
    "https://fonts.googleapis.com",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "data:",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "blob:",
    "https:",
)
CSP_CONNECT_SRC = (
    "'self'",
    "ws:",  # WebSocket
    "wss:",  # Secure WebSocket
)
CSP_MEDIA_SRC = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)  # Disallow Flash and other plugins
CSP_FRAME_ANCESTORS = ("'none'",)  # Prevent clickjacking
CSP_FORM_ACTION = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_UPGRADE_INSECURE_REQUESTS = True  # Upgrade HTTP to HTTPS

# =============================================================================
# Rate Limiting Configuration
# =============================================================================
# Rate limiting helps prevent brute force attacks and API abuse

RATELIMIT_ENABLE = os.getenv('RATELIMIT_ENABLE', 'True').lower() == 'true'
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_FAIL_OPEN = False  # Fail closed - block if cache is unavailable

# Default rate limits
RATELIMIT_DEFAULT_LIMIT = '100/hour'
RATELIMIT_LOGIN_LIMIT = '5/minute'  # Stricter for login attempts
RATELIMIT_API_LIMIT = '1000/hour'

# View-specific rate limits
RATELIMITS = {
    'login': '5/minute',
    'api_anon': '100/hour',
    'api_auth': '1000/hour',
    'password_reset': '3/hour',
    'export': '10/hour',
    'import': '10/hour',
}

# =============================================================================
# Password Validation Rules
# =============================================================================
# Enhanced password validation for production security

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased from default 8 for production
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Custom validators can be added here
]

# =============================================================================
# Session Security Settings
# =============================================================================

# Session settings for production
SESSION_COOKIE_NAME = 'ptms_sessionid'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_COOKIE_SECURE = True  # Only send over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Refresh expiry on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# =============================================================================
# CSRF Security Settings
# =============================================================================

CSRF_COOKIE_NAME = 'ptms_csrftoken'
CSRF_COOKIE_SECURE = True  # Only send over HTTPS
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = False  # Store in cookie, not session
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = []  # Set in production settings from env

# =============================================================================
# Additional Security Headers
# =============================================================================

# Security middleware settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_SSL_REDIRECT = True

# =============================================================================
# Trusted Hosts and Origins
# =============================================================================

# These should be configured in production.py from environment variables
TRUSTED_ORIGINS = []
ALLOWED_HOSTS = []

# =============================================================================
# Account Security Settings
# =============================================================================

# Login security
LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes lockout after failed attempts

# Password reset security
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
PASSWORD_RESET_ATTEMPTS_LIMIT = 3

# Account lockout
ACCOUNT_LOCKOUT_ENABLED = True
ACCOUNT_LOCKOUT_DURATION = 1800  # 30 minutes
ACCOUNT_LOCKOUT_MAX_ATTEMPTS = 5

# =============================================================================
# API Security Settings
# =============================================================================

# API throttling
REST_FRAMEWORK_THROTTLE_RATES = {
    'anon': '100/hour',
    'user': '1000/hour',
    'login': '5/minute',
    'password_reset': '3/hour',
}

# JWT settings (if using JWT authentication)
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': 1800,  # 30 minutes
    'JWT_REFRESH_EXPIRATION_DELTA': 604800,  # 7 days
    'JWT_ALLOW_REFRESH': True,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

# =============================================================================
# File Upload Security
# =============================================================================

# Allowed file types for upload
ALLOWED_UPLOAD_EXTENSIONS = [
    '.csv', '.xlsx', '.xls',  # Import files
    '.pdf', '.doc', '.docx',  # Documents
    '.png', '.jpg', '.jpeg', '.gif',  # Images
]

# Maximum file sizes (in bytes)
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB
MAX_IMPORT_SIZE = 10 * 1024 * 1024  # 10MB for imports

# File type validation
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# =============================================================================
# Audit and Logging Security
# =============================================================================

# Enable audit logging
AUDIT_LOG_ENABLED = True
AUDIT_LOG_SENSITIVE_FIELDS = [
    'password',
    'token',
    'secret',
    'credit_card',
    'ssn',
    'api_key',
]

# Security event logging
SECURITY_LOG_ENABLED = True
SECURITY_LOG_EVENTS = [
    'login_failed',
    'login_success',
    'logout',
    'password_change',
    'password_reset_request',
    'password_reset_complete',
    'account_locked',
    'permission_denied',
    'suspicious_activity',
]
