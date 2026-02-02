"""
Common views for Project Tracking Management System.

This module contains shared views including:
- Health check endpoint
- API status endpoint
- System information endpoints
"""

import os
import time
import psutil
from datetime import datetime
from typing import Dict, Any

from django.db import connection, DatabaseError
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring system status.
    
    Checks:
    - Database connectivity
    - Redis connectivity
    - Disk space
    - Response time
    
    GET /health/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Perform health checks and return status."""
        start_time = time.time()
        
        checks = {
            'database': self._check_database(),
            'redis': self._check_redis(),
            'disk': self._check_disk_space(),
            'memory': self._check_memory(),
        }
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Determine overall status
        all_healthy = all(check.get('healthy', False) for check in checks.values())
        
        status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        response_data = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': getattr(settings, 'DJANGO_ENV', 'production'),
            'response_time_ms': round(response_time, 2),
            'checks': checks,
        }
        
        return Response(response_data, status=status_code)
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                # Get database info
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0] if cursor.fetchone() else "Unknown"
                
                return {
                    'healthy': True,
                    'message': 'Database connection successful',
                    'details': {
                        'engine': connection.vendor,
                        'version': version[:50] if version else 'Unknown',
                    }
                }
        except DatabaseError as e:
            return {
                'healthy': False,
                'message': f'Database connection failed: {str(e)}',
                'details': {}
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Database check error: {str(e)}',
                'details': {}
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            # Try to set and get a test value
            test_key = '_health_check_test'
            cache.set(test_key, 'ok', timeout=5)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            if value == 'ok':
                return {
                    'healthy': True,
                    'message': 'Redis connection successful',
                    'details': {
                        'backend': settings.CACHES['default'].get('BACKEND', 'Unknown'),
                    }
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Redis test value mismatch',
                    'details': {}
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Redis connection failed: {str(e)}',
                'details': {}
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage."""
        try:
            # Check multiple paths
            paths_to_check = [
                '/',  # Root
                settings.BASE_DIR,  # Project directory
                getattr(settings, 'MEDIA_ROOT', '/tmp'),
                getattr(settings, 'STATIC_ROOT', '/tmp'),
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            paths_to_check = [p for p in paths_to_check if not (p in seen or seen.add(p))]
            
            disk_checks = []
            min_free_percent = 10  # Alert if less than 10% free
            
            for path in paths_to_check:
                if os.path.exists(path):
                    usage = psutil.disk_usage(path)
                    free_percent = (usage.free / usage.total) * 100
                    
                    disk_checks.append({
                        'path': path,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'free_percent': round(free_percent, 2),
                        'healthy': free_percent >= min_free_percent,
                    })
            
            all_healthy = all(d['healthy'] for d in disk_checks)
            
            return {
                'healthy': all_healthy,
                'message': 'Disk space OK' if all_healthy else 'Low disk space warning',
                'details': {
                    'disks': disk_checks,
                    'min_free_percent_required': min_free_percent,
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Disk check error: {str(e)}',
                'details': {}
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check system memory usage."""
        try:
            memory = psutil.virtual_memory()
            
            # Alert if more than 90% memory used
            max_usage_percent = 90
            is_healthy = memory.percent < max_usage_percent
            
            return {
                'healthy': is_healthy,
                'message': 'Memory usage OK' if is_healthy else 'High memory usage warning',
                'details': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percent_used': memory.percent,
                    'max_percent_allowed': max_usage_percent,
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Memory check error: {str(e)}',
                'details': {}
            }


class ReadinessCheckView(APIView):
    """
    Readiness check for Kubernetes/Docker orchestration.
    
    Determines if the application is ready to receive traffic.
    
    GET /ready/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if application is ready."""
        checks = {
            'database': self._check_database(),
            'migrations': self._check_migrations(),
        }
        
        all_ready = all(check for check in checks.values())
        
        status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({
            'ready': all_ready,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': checks,
        }, status=status_code)
    
    def _check_database(self) -> bool:
        """Check if database is accessible."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def _check_migrations(self) -> bool:
        """Check if all migrations have been applied."""
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            
            # Check for unapplied migrations
            plan = executor.migration_plan(targets)
            return len(plan) == 0
        except Exception:
            # If we can't check migrations, assume they're applied
            return True


class LivenessCheckView(APIView):
    """
    Liveness check for Kubernetes/Docker orchestration.
    
    Determines if the application is running (not deadlocked).
    
    GET /live/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Simple liveness check."""
        return Response({
            'alive': True,
            'timestamp': datetime.utcnow().isoformat(),
        })


@method_decorator(csrf_exempt, name='dispatch')
class SystemInfoView(View):
    """
    System information endpoint (for admin/debugging).
    
    Returns non-sensitive system information.
    """
    
    def get(self, request):
        """Return system information."""
        # Only allow authenticated staff users
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({
                'error': 'Permission denied'
            }, status=403)
        
        info = {
            'django': {
                'version': self._get_django_version(),
                'settings_module': os.getenv('DJANGO_SETTINGS_MODULE', 'Unknown'),
            },
            'python': {
                'version': self._get_python_version(),
                'implementation': self._get_python_implementation(),
            },
            'system': {
                'platform': self._get_platform_info(),
                'uptime': self._get_uptime(),
            },
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        return JsonResponse(info)
    
    def _get_django_version(self) -> str:
        """Get Django version."""
        try:
            import django
            return django.get_version()
        except Exception:
            return 'Unknown'
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_python_implementation(self) -> str:
        """Get Python implementation."""
        import platform
        return platform.python_implementation()
    
    def _get_platform_info(self) -> Dict[str, str]:
        """Get platform information."""
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except Exception:
            return 'Unknown'


class APIStatusView(APIView):
    """
    API status and information endpoint.
    
    Returns API version and available endpoints.
    
    GET /api/status/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return API status and information."""
        from django.urls import get_resolver
        
        resolver = get_resolver()
        
        # Get API URL patterns
        api_patterns = []
        try:
            url_patterns = resolver.url_patterns
            for pattern in url_patterns:
                if hasattr(pattern, 'pattern') and 'api' in str(pattern.pattern):
                    api_patterns.append(str(pattern.pattern))
        except Exception:
            pass
        
        return Response({
            'name': 'Project Tracking Management System API',
            'version': getattr(settings, 'API_VERSION', 'v1'),
            'status': 'operational',
            'documentation': '/api/schema/swagger-ui/',
            'endpoints': {
                'health': '/health/',
                'ready': '/ready/',
                'live': '/live/',
                'api': '/api/',
                'admin': '/admin/',
            },
            'timestamp': datetime.utcnow().isoformat(),
        })
