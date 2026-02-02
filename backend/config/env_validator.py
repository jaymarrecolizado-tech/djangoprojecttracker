"""
Environment Variable Validator for Project Tracking Management System.

This module validates that all required environment variables are properly configured
before the application starts. It performs security checks and provides helpful
error messages for missing or invalid configurations.
"""

import os
import sys
from typing import List, Tuple, Optional


class EnvironmentValidationError(Exception):
    """Raised when environment validation fails."""
    pass


class EnvironmentValidator:
    """
    Validates environment variables for production deployment.
    
    Checks:
    - Required environment variables are set
    - SECRET_KEY is strong enough (min 50 chars)
    - Database credentials are provided
    - DEBUG is False in production
    - ALLOWED_HOSTS is configured
    - Security settings are properly configured
    """
    
    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, raise_on_error: bool = True) -> Tuple[List[str], List[str]]:
        """
        Run all validation checks.
        
        Args:
            raise_on_error: If True, raises EnvironmentValidationError on critical errors
            
        Returns:
            Tuple of (errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Run all validation methods
        self._validate_secret_key()
        self._validate_debug_mode()
        self._validate_allowed_hosts()
        self._validate_database_settings()
        self._validate_redis_settings()
        self._validate_email_settings()
        self._validate_security_settings()
        self._validate_cors_settings()
        self._validate_file_upload_settings()
        self._validate_logging_settings()
        
        if self.errors and raise_on_error:
            error_message = "\n".join([
                "Environment validation failed!",
                "=" * 50,
                "CRITICAL ERRORS:",
                "- " + "\n- ".join(self.errors),
                "",
                "Please fix these issues before starting the application.",
                "See docs/PRODUCTION_DEPLOYMENT.md for setup instructions."
            ])
            raise EnvironmentValidationError(error_message)
        
        return self.errors, self.warnings
    
    def _validate_secret_key(self) -> None:
        """Validate SECRET_KEY is strong enough."""
        secret_key = os.getenv('SECRET_KEY', '')
        
        if not secret_key:
            self.errors.append("SECRET_KEY is not set. Set a strong secret key.")
        elif len(secret_key) < 50:
            self.errors.append(
                f"SECRET_KEY is too short ({len(secret_key)} chars). "
                "Minimum 50 characters required for production security."
            )
        elif 'django-insecure' in secret_key or 'change-me' in secret_key.lower():
            self.errors.append(
                "SECRET_KEY appears to be using default/placeholder value. "
                "Generate a new secure key for production."
            )
    
    def _validate_debug_mode(self) -> None:
        """Validate DEBUG is disabled in production."""
        debug = os.getenv('DEBUG', 'False').lower()
        
        if debug in ('true', '1', 'yes', 'on'):
            if self.environment == 'production':
                self.errors.append(
                    "DEBUG is set to True in production environment. "
                    "Set DEBUG=False for production deployments."
                )
            else:
                self.warnings.append("DEBUG is enabled. Disable for production.")
    
    def _validate_allowed_hosts(self) -> None:
        """Validate ALLOWED_HOSTS is properly configured."""
        allowed_hosts = os.getenv('ALLOWED_HOSTS', '').strip()
        
        if not allowed_hosts:
            self.errors.append(
                "ALLOWED_HOSTS is not set. "
                "Add your domain names (e.g., 'example.com,www.example.com')."
            )
        else:
            hosts = [h.strip() for h in allowed_hosts.split(',') if h.strip()]
            
            if not hosts:
                self.errors.append("ALLOWED_HOSTS is empty after parsing.")
            elif '*' in hosts and self.environment == 'production':
                self.errors.append(
                    "ALLOWED_HOSTS contains '*' wildcard which is insecure for production. "
                    "Specify exact domain names."
                )
            elif 'localhost' in hosts and len(hosts) == 1:
                self.warnings.append(
                    "ALLOWED_HOSTS only contains localhost. "
                    "Add your production domain names."
                )
    
    def _validate_database_settings(self) -> None:
        """Validate database configuration."""
        required_db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
        
        for var in required_db_vars:
            value = os.getenv(var, '').strip()
            if not value:
                self.errors.append(f"{var} is not set. Database configuration incomplete.")
        
        # Check for default/test credentials
        db_password = os.getenv('DB_PASSWORD', '')
        weak_passwords = ['password', '123456', 'admin', 'root', 'secret']
        
        if db_password.lower() in weak_passwords:
            self.warnings.append(
                "Database password appears to be weak. "
                "Use a strong password in production."
            )
    
    def _validate_redis_settings(self) -> None:
        """Validate Redis configuration."""
        redis_host = os.getenv('REDIS_HOST', '')
        
        if not redis_host:
            self.warnings.append(
                "REDIS_HOST is not set. "
                "Redis is required for caching, sessions, and WebSocket support."
            )
    
    def _validate_email_settings(self) -> None:
        """Validate email configuration for production."""
        if self.environment == 'production':
            email_backend = os.getenv('EMAIL_BACKEND', '')
            
            if 'console' in email_backend:
                self.warnings.append(
                    "EMAIL_BACKEND is set to console backend. "
                    "Configure SMTP for production email delivery."
                )
            
            required_email_vars = ['EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
            for var in required_email_vars:
                if not os.getenv(var, '').strip():
                    self.warnings.append(f"{var} is not set. Email notifications may not work.")
    
    def _validate_security_settings(self) -> None:
        """Validate security-related settings."""
        if self.environment == 'production':
            # Check CSRF cookie security
            csrf_secure = os.getenv('CSRF_COOKIE_SECURE', '').lower()
            if csrf_secure not in ('true', '1', 'yes', 'on'):
                self.warnings.append(
                    "CSRF_COOKIE_SECURE is not set to True. "
                    "CSRF cookies will not be sent over HTTPS only."
                )
            
            # Check session cookie security
            session_secure = os.getenv('SESSION_COOKIE_SECURE', '').lower()
            if session_secure not in ('true', '1', 'yes', 'on'):
                self.warnings.append(
                    "SESSION_COOKIE_SECURE is not set to True. "
                    "Session cookies will not be sent over HTTPS only."
                )
    
    def _validate_cors_settings(self) -> None:
        """Validate CORS configuration."""
        cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').strip()
        
        if not cors_origins:
            if self.environment == 'production':
                self.errors.append(
                    "CORS_ALLOWED_ORIGINS is not set. "
                    "Frontend requests will be blocked."
                )
        elif '*' in cors_origins:
            self.warnings.append(
                "CORS_ALLOWED_ORIGINS contains wildcard. "
                "This is insecure for production. Specify exact origins."
            )
    
    def _validate_file_upload_settings(self) -> None:
        """Validate file upload configuration."""
        media_root = os.getenv('MEDIA_ROOT', '')
        static_root = os.getenv('STATIC_ROOT', '')
        
        if not media_root:
            self.warnings.append("MEDIA_ROOT is not set. File uploads will not work.")
        
        if not static_root:
            self.warnings.append("STATIC_ROOT is not set. Static files will not be collected.")
    
    def _validate_logging_settings(self) -> None:
        """Validate logging configuration."""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        if log_level not in valid_levels:
            self.warnings.append(
                f"LOG_LEVEL '{log_level}' is invalid. "
                f"Use one of: {', '.join(valid_levels)}"
            )
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print("=" * 50)
        print("Environment Validation Summary")
        print("=" * 50)
        print(f"Environment: {self.environment}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n❌ CRITICAL ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        
        print("=" * 50)


def validate_environment(environment: Optional[str] = None) -> bool:
    """
    Convenience function to validate environment.
    
    Args:
        environment: Environment name (defaults to DJANGO_ENV or 'production')
        
    Returns:
        True if validation passed, False otherwise
    """
    if environment is None:
        environment = os.getenv('DJANGO_ENV', 'production')
    
    validator = EnvironmentValidator(environment=environment)
    
    try:
        errors, warnings = validator.validate(raise_on_error=False)
        validator.print_summary()
        return len(errors) == 0
    except Exception as e:
        print(f"Validation error: {e}")
        return False


# Run validation when module is executed directly
if __name__ == '__main__':
    success = validate_environment()
    sys.exit(0 if success else 1)
