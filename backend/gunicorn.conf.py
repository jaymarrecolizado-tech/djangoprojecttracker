"""
Gunicorn configuration for Project Tracking Management System.

This module contains production-optimized Gunicorn settings.
For more information, see: https://docs.gunicorn.org/en/stable/configure.html
"""

import os
import multiprocessing

# =============================================================================
# Server Socket Configuration
# =============================================================================

# The socket to bind to
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# Number of pending connections
backlog = int(os.getenv('GUNICORN_BACKLOG', '2048'))

# =============================================================================
# Worker Processes Configuration
# =============================================================================

# Number of worker processes
# Formula: (2 x $num_cores) + 1
# This can be overridden by GUNICORN_WORKERS environment variable
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker class
# Options: sync, gevent, eventlet
# gevent is recommended for high concurrency (WebSocket support)
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')

# Number of worker threads (only used with gthread worker class)
threads = int(os.getenv('GUNICORN_THREADS', '4'))

# Maximum number of simultaneous clients per worker (for gevent/eventlet)
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))

# Maximum number of requests a worker will process before restarting
# This helps prevent memory leaks
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '10000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '1000'))

# Timeout for graceful workers restart
# After receiving a restart signal, workers have this much time to finish
# serving requests before they are force-killed
timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))

# The number of seconds to wait for the next request on a Keep-Alive HTTP
# connection
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))

# Workers silent for more than this many seconds are killed and restarted
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '120'))

# =============================================================================
# Server Mechanics Configuration
# =============================================================================

# The type of workers to use
# sync: synchronous workers
# gevent: asynchronous workers using gevent
# eventlet: asynchronous workers using eventlet
# gthread: threaded workers
# tornado: tornado workers

# Reload workers when code changes (development only, disable in production)
reload = os.getenv('GUNICORN_RELOAD', 'False').lower() == 'true'

# The maximum size of HTTP request line in bytes
limit_request_line = int(os.getenv('GUNICORN_LIMIT_REQUEST_LINE', '4094'))

# Limit the allowed size of an HTTP request header field
limit_request_fields = int(os.getenv('GUNICORN_LIMIT_REQUEST_FIELDS', '100'))

# Limit the allowed size of an HTTP request header field
limit_request_field_size = int(os.getenv('GUNICORN_LIMIT_REQUEST_FIELD_SIZE', '8190'))

# =============================================================================
# Logging Configuration
# =============================================================================

# Access log - records incoming HTTP requests
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
# '-' means log to stdout
# Set to a file path to log to file
# Set to None to disable access logging

# Error log - records Gunicorn server errors
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
# '-' means log to stderr

# Log level
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
# Options: debug, info, warning, error, critical

# Access log format
access_log_format = os.getenv(
    'GUNICORN_ACCESS_LOG_FORMAT',
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
)
# Format variables:
#   h: remote address
#   l: '-' (ident)
#   u: user name
#   t: date of the request
#   r: status line (e.g. GET / HTTP/1.1)
#   s: status code
#   b: response length or '-'
#   f: referer
#   a: user agent
#   D: request time in microseconds
#   T: request time in seconds
#   p: process ID
#   {Header}i: request header
#   {Header}o: response header

# Whether to send Django output to the error log
capture_output = True

# Whether to send output to syslog
syslog = False

# Syslog address
syslog_addr = 'udp://localhost:514'

# Syslog facility
syslog_facility = 'user'

# Process name in syslog
proc_name = 'ptms'

# =============================================================================
# Process Naming
# =============================================================================

# A base to use with setproctitle for process naming
# default: None
default_proc_name = 'ptms'

# =============================================================================
# SSL Configuration (if not using reverse proxy like Nginx)
# =============================================================================

# SSL key file
keyfile = os.getenv('GUNICORN_SSL_KEYFILE', None)

# SSL certificate file
certfile = os.getenv('GUNICORN_SSL_CERTFILE', None)

# SSL version
ssl_version = os.getenv('GUNICORN_SSL_VERSION', 'TLSv1_2')

# SSL cipher list
ciphers = os.getenv(
    'GUNICORN_SSL_CIPHERS',
    'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384'
)

# =============================================================================
# Server Hooks
# =============================================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_reload(server):
    """Called when receiving a SIGHUP signal."""
    pass


def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn server ready with {workers} {worker_class} workers")


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    pass


def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    pass


def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Gunicorn server shutting down")


def worker_exit(server, worker):
    """Called just after a worker has been exited, in the master process."""
    pass


# =============================================================================
# Preload Application
# =============================================================================

# Load application code before the worker processes are forked
# This reduces memory usage and startup time
preload_app = True


def post_worker_init(worker):
    """Called just after a worker has been forked."""
    # You can initialize worker-specific resources here
    pass


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    # Reconnect to database after forking to avoid connection sharing issues
    # This is important for some database drivers
    pass


# =============================================================================
# Django-Specific Configuration
# =============================================================================

# Set Django settings module
raw_env = [
    f"DJANGO_SETTINGS_MODULE=config.settings.production",
]

# =============================================================================
# Security Configuration
# =============================================================================

# Forwarded allow IPs (for use behind reverse proxy)
forwarded_allow_ips = os.getenv('GUNICORN_FORWARDED_ALLOW_IPS', '*')

# Secure scheme headers (for use behind reverse proxy)
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Proxy protocol
proxy_protocol = False

# Proxy allow IPs
proxy_allow_ips = os.getenv('GUNICORN_PROXY_ALLOW_IPS', '*')

# =============================================================================
# Temporary Files
# =============================================================================

# Directory to store temporary request data
# default: None (system default)
tmp_upload_dir = os.getenv('GUNICORN_TMP_UPLOAD_DIR', None)

# =============================================================================
# Performance Tuning Notes
# =============================================================================
"""
Worker Class Selection:

1. sync (default):
   - Best for: CPU-bound applications
   - Pros: Simple, predictable
   - Cons: One request per worker at a time
   
2. gevent:
   - Best for: I/O-bound applications, WebSocket support
   - Pros: High concurrency, lightweight
   - Cons: Requires monkey patching, may have compatibility issues
   
3. gthread:
   - Best for: Thread-safe applications
   - Pros: Multiple threads per worker
   - Cons: GIL limits true parallelism
   
4. eventlet:
   - Best for: Similar to gevent
   - Pros: Pure Python
   - Cons: Slightly slower than gevent

For PTMS with WebSocket support, gevent is recommended.

Memory Usage Calculation:
- Base memory: ~50MB per worker
- With gevent: ~75MB per worker
- Total = Base + (workers × Worker Memory)

Example for 4-core server:
- workers = (2 × 4) + 1 = 9
- Memory = 50MB + (9 × 75MB) = ~725MB
"""
