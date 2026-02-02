"""
Structured logging configuration for Project Tracking Management System.

This module provides:
- JSON structured logging for production
- Log rotation configuration
- Separate log files for different log types
- Sentry integration (optional)
- Security and audit logging
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, Any


# =============================================================================
# Log Directory Configuration
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(os.getenv('LOG_DIR', BASE_DIR / 'logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Log File Paths
# =============================================================================

LOG_FILES = {
    'application': LOG_DIR / 'application.log',
    'error': LOG_DIR / 'error.log',
    'security': LOG_DIR / 'security.log',
    'audit': LOG_DIR / 'audit.log',
    'performance': LOG_DIR / 'performance.log',
    'celery': LOG_DIR / 'celery.log',
}

# =============================================================================
# JSON Formatter for Structured Logging
# =============================================================================

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs logs in JSON format for easier parsing and analysis.
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        self.default_fields = kwargs
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process,
        }
        
        # Add default fields
        log_data.update(self.default_fields)
        
        # Add extra fields from record
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class PrettyFormatter(logging.Formatter):
    """
    Pretty formatter for development and console output.
    """
    
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format."""
        return (
            f"[{self.formatTime(record)}] "
            f"{record.levelname:8s} "
            f"{record.name:20s} "
            f"{record.getMessage()}"
        )


# =============================================================================
# Logging Configuration Dictionary
# =============================================================================

def get_logging_config(debug: bool = False) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        debug: Whether to use debug logging configuration
        
    Returns:
        Logging configuration dictionary
    """
    
    # Determine formatter based on environment
    if debug:
        formatter_class = 'logging.formatters.PrettyFormatter'
        formatter_config = {
            'format': '{asctime} [{levelname:8s}] {name:20s} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    else:
        formatter_config = {
            '()': 'backend.config.logging.JSONFormatter',
            'environment': os.getenv('DJANGO_ENV', 'production'),
            'service': 'project-tracking',
            'version': os.getenv('APP_VERSION', '1.0.0'),
        }
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': formatter_config,
            'verbose': {
                'format': '{asctime} [{levelname:8s}] {name:20s} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[{levelname}] {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose' if debug else 'json',
                'level': 'DEBUG' if debug else 'INFO',
            },
            'application_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOG_FILES['application']),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'json',
                'level': 'INFO',
                'encoding': 'utf-8',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOG_FILES['error']),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'json',
                'level': 'ERROR',
                'encoding': 'utf-8',
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOG_FILES['security']),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'json',
                'level': 'INFO',
                'encoding': 'utf-8',
            },
            'audit_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': str(LOG_FILES['audit']),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 90,  # 90 days
                'formatter': 'json',
                'level': 'INFO',
                'encoding': 'utf-8',
            },
            'celery_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOG_FILES['celery']),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'level': 'INFO',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'application_file', 'error_file'],
                'level': 'DEBUG' if debug else 'INFO',
                'propagate': False,
            },
            'django': {
                'handlers': ['console', 'application_file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['security_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG' if debug else 'WARNING',
                'propagate': False,
            },
            'apps': {
                'handlers': ['console', 'application_file'],
                'level': 'DEBUG' if debug else 'INFO',
                'propagate': False,
            },
            'apps.audit': {
                'handlers': ['audit_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'apps.security': {
                'handlers': ['security_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery': {
                'handlers': ['celery_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery.task': {
                'handlers': ['celery_file'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    return config


# =============================================================================
# Sentry Integration
# =============================================================================

def init_sentry() -> None:
    """
    Initialize Sentry for error tracking.
    
    Sentry DSN should be set in environment variable SENTRY_DSN.
    """
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if not sentry_dsn:
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
            ],
            # Performance monitoring
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            # Profiling (requires sentry-sdk>=1.18.0)
            profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
            # Environment
            environment=os.getenv('DJANGO_ENV', 'production'),
            release=os.getenv('APP_VERSION', '1.0.0'),
            # Send default PII (personally identifiable information)
            send_default_pii=True,
            # Before send hook to filter sensitive data
            before_send=lambda event, hint: _filter_sensitive_data(event),
        )
        
        print(f"✅ Sentry initialized for environment: {os.getenv('DJANGO_ENV', 'production')}")
        
    except ImportError:
        print("⚠️  Sentry SDK not installed. Skipping Sentry initialization.")


def _filter_sensitive_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter sensitive data before sending to Sentry.
    
    Args:
        event: Sentry event dictionary
        
    Returns:
        Filtered event dictionary
    """
    sensitive_keys = [
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'auth', 'cookie', 'sessionid',
        'csrfmiddlewaretoken', 'credit_card', 'ssn',
    ]
    
    def _filter_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive keys from dictionary."""
        filtered = {}
        for key, value in d.items():
            lower_key = key.lower()
            if any(sensitive in lower_key for sensitive in sensitive_keys):
                filtered[key] = '[FILTERED]'
            elif isinstance(value, dict):
                filtered[key] = _filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    _filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        return filtered
    
    # Filter request data if present
    if 'request' in event and isinstance(event['request'], dict):
        if 'data' in event['request']:
            event['request']['data'] = _filter_dict(event['request']['data'])
        if 'headers' in event['request']:
            event['request']['headers'] = _filter_dict(event['request']['headers'])
        if 'cookies' in event['request']:
            event['request']['cookies'] = _filter_dict(event['request']['cookies'])
    
    # Filter extra data
    if 'extra' in event and isinstance(event['extra'], dict):
        event['extra'] = _filter_dict(event['extra'])
    
    return event


# =============================================================================
# Audit Logger
# =============================================================================

class AuditLogger:
    """
    Logger for audit events.
    
    Tracks important security and business events.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('apps.audit')
    
    def log_login(self, user_id: str, ip_address: str, success: bool, **kwargs):
        """Log login attempt."""
        self.logger.info(
            'Login attempt',
            extra={
                'event_type': 'login',
                'user_id': user_id,
                'ip_address': ip_address,
                'success': success,
                **kwargs
            }
        )
    
    def log_logout(self, user_id: str, ip_address: str, **kwargs):
        """Log logout."""
        self.logger.info(
            'Logout',
            extra={
                'event_type': 'logout',
                'user_id': user_id,
                'ip_address': ip_address,
                **kwargs
            }
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str, **kwargs):
        """Log data access."""
        self.logger.info(
            'Data access',
            extra={
                'event_type': 'data_access',
                'user_id': user_id,
                'resource': resource,
                'action': action,
                **kwargs
            }
        )
    
    def log_permission_denied(self, user_id: str, resource: str, action: str, **kwargs):
        """Log permission denied."""
        self.logger.warning(
            'Permission denied',
            extra={
                'event_type': 'permission_denied',
                'user_id': user_id,
                'resource': resource,
                'action': action,
                **kwargs
            }
        )


# Global audit logger instance
audit_logger = AuditLogger()


# =============================================================================
# Performance Logger
# =============================================================================

class PerformanceLogger:
    """
    Logger for performance metrics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('apps.performance')
    
    def log_query_time(self, query: str, duration_ms: float, **kwargs):
        """Log slow query."""
        self.logger.info(
            'Query executed',
            extra={
                'event_type': 'query',
                'query': query[:1000],  # Truncate long queries
                'duration_ms': duration_ms,
                **kwargs
            }
        )
    
    def log_request_time(self, path: str, method: str, duration_ms: float, status_code: int, **kwargs):
        """Log request processing time."""
        self.logger.info(
            'Request processed',
            extra={
                'event_type': 'request',
                'path': path,
                'method': method,
                'duration_ms': duration_ms,
                'status_code': status_code,
                **kwargs
            }
        )


# Global performance logger instance
performance_logger = PerformanceLogger()
