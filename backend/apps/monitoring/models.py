"""
Models for the monitoring app.
"""

from django.db import models
from django.conf import settings


class Metric(models.Model):
    """
    Stores system and application metrics.
    """
    
    METRIC_TYPES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('network', 'Network Usage'),
        ('request_time', 'Request Time'),
        ('query_time', 'Query Time'),
        ('error_rate', 'Error Rate'),
        ('queue_size', 'Queue Size'),
    ]
    
    name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
            models.Index(fields=['name', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value}{self.unit} at {self.timestamp}"


class Alert(models.Model):
    """
    Stores monitoring alerts.
    """
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    metric = models.ForeignKey(Metric, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class PerformanceLog(models.Model):
    """
    Stores detailed performance logs.
    """
    
    url = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    duration_ms = models.FloatField()
    status_code = models.IntegerField()
    user_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    query_count = models.IntegerField(default=0)
    query_time_ms = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.url} - {self.duration_ms}ms"


class SystemEvent(models.Model):
    """
    Stores system events and incidents.
    """
    
    EVENT_TYPES = [
        ('deployment', 'Deployment'),
        ('restart', 'Restart'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
        ('backup', 'Backup'),
        ('scaling', 'Scaling'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type}: {self.description[:50]}"
