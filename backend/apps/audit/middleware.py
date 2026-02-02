"""Middleware for audit logging."""
import json
import re
from django.db import connection
from .models import AuditLog


class AuditLogMiddleware:
    """Middleware to log requests."""
    
    SENSITIVE_FIELDS = {'password', 'secret', 'token', 'api_key', 'credential'}
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store old values for comparison
        request._audit_old_values = {}
        
        response = self.get_response(request)
        
        if request.user and request.user.is_authenticated:
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                self.log_action(request, response)
        
        return response
    
    def log_action(self, request, response):
        """Log the action with old and new values."""
        # Extract model name from path
        model_name = self._extract_model_name(request.path)
        
        # Get action type
        action_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        action = action_map.get(request.method, 'VIEW')
        
        # Parse request body for new values
        new_values = self._parse_request_body(request)
        
        # Create audit log
        AuditLog.objects.create(
            action=action,
            model_name=model_name,
            object_id=self._extract_object_id(request.path),
            old_values=request._audit_old_values.get(model_name, {}),
            new_values=new_values,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            user=request.user if request.user.is_authenticated else None,
            status_code=getattr(response, 'status_code', None)
        )
    
    def _extract_model_name(self, path):
        """Extract model name from URL path."""
        # Remove leading/trailing slashes and split by '/'
        parts = [p for p in path.strip('/').split('/') if p]
        
        # Common patterns to skip
        skip_patterns = {'api', 'v1', 'v2', 'admin', 'auth', 'oauth'}
        
        for part in reversed(parts):
            # Skip version numbers and common prefixes
            if part in skip_patterns or part.isdigit():
                continue
            # Check if it looks like an ID (UUID or integer)
            if self._is_id(part):
                continue
            # Return the model name in singular form
            return self._to_singular(part)
        
        return path
    
    def _is_id(self, value):
        """Check if value looks like an ID."""
        # UUID pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, value.lower()):
            return True
        # Integer pattern
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _to_singular(self, word):
        """Convert plural to singular."""
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('es') and len(word) > 3:
            return word[:-2]
        elif word.endswith('s') and len(word) > 1:
            return word[:-1]
        return word
    
    def _extract_object_id(self, path):
        """Extract object ID from URL path."""
        parts = [p for p in path.strip('/').split('/') if p]
        for part in reversed(parts):
            if self._is_id(part):
                return part
        return None
    
    def _parse_request_body(self, request):
        """Parse request body for new values."""
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body.decode('utf-8'))
                return self._sanitize_data(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
        elif request.content_type == 'application/x-www-form-urlencoded':
            return dict(request.POST)
        return {}
    
    def _sanitize_data(self, data, depth=0):
        """Remove sensitive fields from data."""
        if depth > 5:  # Prevent deep recursion
            return data
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Skip sensitive fields
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    continue
                # Skip internal fields
                if key.startswith('_'):
                    continue
                result[key] = self._sanitize_data(value, depth + 1)
            return result
        elif isinstance(data, list):
            return [self._sanitize_data(item, depth + 1) for item in data]
        else:
            return data
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class AuditMiddleware:
    """Alternative audit middleware that can be used in MIDDLEWARE setting."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Initialize audit tracking
        request._audit_data = {}
        
        response = self.get_response(request)
        
        # Log after response is generated
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                self._log_request(request, response)
        
        return response
    
    def _log_request(self, request, response):
        """Log the request to audit log."""
        from django.db import connection
        
        # Only log if we have a successful response
        if response.status_code >= 400:
            return
        
        # Extract model name
        model_name = self._get_model_name(request)
        
        # Create audit log
        AuditLog.objects.create(
            action=self._get_action(request.method),
            model_name=model_name,
            object_id=self._get_object_id(request),
            new_values=self._get_request_data(request),
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            user=request.user if request.user.is_authenticated else None,
            status_code=response.status_code
        )
    
    def _get_model_name(self, request):
        """Get model name from request path."""
        path = request.path
        parts = [p for p in path.strip('/').split('/') if p]
        
        # Skip common prefixes
        skip = {'api', 'v1', 'v2', 'admin', 'auth'}
        model_parts = []
        
        for part in parts:
            if part in skip or part.isdigit():
                continue
            if self._is_uuid(part):
                continue
            model_parts.append(part)
        
        if model_parts:
            return model_parts[-1].rstrip('s')  # Remove trailing 's' for singular
        return 'unknown'
    
    def _is_uuid(self, value):
        """Check if value is a UUID."""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value.lower()))
    
    def _get_action(self, method):
        """Map HTTP method to action type."""
        actions = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        return actions.get(method, 'VIEW')
    
    def _get_object_id(self, request):
        """Extract object ID from request path."""
        parts = [p for p in request.path.strip('/').split('/') if p]
        for part in reversed(parts):
            if self._is_uuid(part) or part.isdigit():
                return part
        return None
    
    def _get_request_data(self, request):
        """Get request data for logging."""
        import json
        if request.content_type == 'application/json':
            try:
                return json.loads(request.body.decode('utf-8'))
            except:
                return {}
        return dict(request.POST)
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
