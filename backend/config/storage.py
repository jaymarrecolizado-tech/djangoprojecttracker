"""
Storage configuration for Project Tracking Management System.

This module contains configurations for:
- WhiteNoise static files serving
- S3/MinIO media files storage (optional)
- Static files compression and caching headers
"""

import os
from typing import Optional

# =============================================================================
# WhiteNoise Configuration
# =============================================================================
# WhiteNoise is used to serve static files directly from Django in production

# Storage backend for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise settings
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False  # Disable in production for better performance
WHITENOISE_MIMETYPES = {
    '.svg': 'image/svg+xml',
    '.woff2': 'font/woff2',
    '.woff': 'font/woff',
    '.ttf': 'font/ttf',
}

# Enable gzip and brotli compression
WHITENOISE_GZIP = True
WHITENOISE_BROTLI = True

# Cache static files for 1 year (immutable files with hash in filename)
WHITENOISE_STATIC_MAX_AGE = 31536000  # 1 year in seconds

# =============================================================================
# Static Files Configuration
# =============================================================================

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('STATIC_ROOT', '/var/www/project_tracking/staticfiles')

# Additional static file directories
STATICFILES_DIRS = [
    # Add any additional static directories here
]

# Static file finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# =============================================================================
# Media Files Configuration
# =============================================================================

MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/var/www/project_tracking/media')

# Maximum upload sizes
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('DATA_UPLOAD_MAX_MEMORY_SIZE', '26214400'))  # 25MB
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('FILE_UPLOAD_MAX_MEMORY_SIZE', '26214400'))  # 25MB

# Upload handlers
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Temporary file upload directory
FILE_UPLOAD_TEMP_DIR = os.getenv('FILE_UPLOAD_TEMP_DIR', '/tmp')

# File upload permissions
FILE_UPLOAD_PERMISSIONS = 0o644  # rw-r--r--
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # rwxr-xr-x

# =============================================================================
# S3/MinIO Configuration (Optional)
# =============================================================================
# Uncomment and configure to use S3 or MinIO for media file storage

# USE_S3_STORAGE = os.getenv('USE_S3_STORAGE', 'False').lower() == 'true'
# USE_MINIO = os.getenv('USE_MINIO', 'False').lower() == 'true'

# if USE_S3_STORAGE or USE_MINIO:
#     # AWS/MinIO Settings
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'project-tracking')
#     AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
#     
#     # MinIO specific settings
#     if USE_MINIO:
#         AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', 'http://localhost:9000')
#         AWS_S3_ADDRESSING_STYLE = 'path'
#     else:
#         AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', None)
#     
#     # S3 Object Parameters
#     AWS_S3_OBJECT_PARAMETERS = {
#         'CacheControl': 'max-age=86400',  # 1 day cache
#     }
#     
#     # Disable querystring authentication for public files
#     AWS_QUERYSTRING_AUTH = False
#     
#     # Default ACL
#     AWS_DEFAULT_ACL = 'public-read'
#     
#     # Static and Media files configuration for S3
#     if USE_S3_STORAGE:
#         # Store static files on S3
#         STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#         STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
#     
#     # Always store media files on S3 when enabled
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'

# =============================================================================
# CDN Configuration (Optional)
# =============================================================================
# Configure CloudFront or other CDN for static/media files

# CDN_DOMAIN = os.getenv('CDN_DOMAIN', '')
# if CDN_DOMAIN:
#     STATIC_URL = f'https://{CDN_DOMAIN}/static/'
#     MEDIA_URL = f'https://{CDN_DOMAIN}/media/'

# =============================================================================
# Security Headers for Static/Media Files
# =============================================================================

# Security headers to be added by WhiteNoise
WHITENOISE_ADD_HEADERS_FUNCTION = None  # Use default or provide custom function

# Custom security headers middleware (if needed)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# =============================================================================
# Storage Health Check
# =============================================================================

def check_storage_health() -> dict:
    """
    Check the health of storage systems.
    
    Returns:
        Dictionary with health check results
    """
    import os
    from pathlib import Path
    
    results = {
        'static_root': {'exists': False, 'writable': False, 'path': STATIC_ROOT},
        'media_root': {'exists': False, 'writable': False, 'path': MEDIA_ROOT},
        'temp_dir': {'exists': False, 'writable': False, 'path': FILE_UPLOAD_TEMP_DIR},
    }
    
    # Check static root
    static_path = Path(STATIC_ROOT)
    results['static_root']['exists'] = static_path.exists()
    if static_path.exists():
        results['static_root']['writable'] = os.access(static_path, os.W_OK)
    
    # Check media root
    media_path = Path(MEDIA_ROOT)
    results['media_root']['exists'] = media_path.exists()
    if media_path.exists():
        results['media_root']['writable'] = os.access(media_path, os.W_OK)
    
    # Check temp directory
    temp_path = Path(FILE_UPLOAD_TEMP_DIR)
    results['temp_dir']['exists'] = temp_path.exists()
    if temp_path.exists():
        results['temp_dir']['writable'] = os.access(temp_path, os.W_OK)
    
    # Determine overall health
    all_healthy = all(
        r['exists'] and r['writable'] 
        for r in results.values()
    )
    
    return {
        'healthy': all_healthy,
        'checks': results,
    }


# =============================================================================
# Cleanup Configuration
# =============================================================================

# Temporary file cleanup settings
FILE_UPLOAD_CLEANUP_AGE = 86400  # 24 hours - files older than this are cleaned up

# =============================================================================
# Import Export Storage Settings
# =============================================================================

# Storage location for import/export temporary files
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'django.core.files.storage.FileSystemStorage'
IMPORT_EXPORT_USE_TRANSACTIONS = True

# =============================================================================
# Logging Configuration for Storage
# =============================================================================

# Log storage-related errors
STORAGE_LOG_LEVEL = os.getenv('STORAGE_LOG_LEVEL', 'WARNING')
