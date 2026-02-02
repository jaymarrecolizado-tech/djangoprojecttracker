"""
Views for the monitoring app.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Metric, Alert, PerformanceLog, SystemEvent


class DashboardView(APIView):
    """
    Monitoring dashboard data.
    
    GET /api/monitoring/dashboard/
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Return dashboard statistics."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # System metrics
        system_metrics = self._get_system_metrics(last_24h)
        
        # Application metrics
        app_metrics = self._get_application_metrics(last_24h)
        
        # Recent alerts
        recent_alerts = Alert.objects.filter(
            created_at__gte=last_24h
        ).order_by('-created_at')[:10]
        
        # Performance statistics
        performance_stats = self._get_performance_stats(last_24h)
        
        # Recent events
        recent_events = SystemEvent.objects.order_by('-created_at')[:10]
        
        return Response({
            'timestamp': now.isoformat(),
            'system_metrics': system_metrics,
            'application_metrics': app_metrics,
            'alerts': self._serialize_alerts(recent_alerts),
            'performance': performance_stats,
            'events': self._serialize_events(recent_events),
        })
    
    def _get_system_metrics(self, since: datetime) -> Dict[str, Any]:
        """Get system metrics for the given time period."""
        metrics = Metric.objects.filter(
            metric_type__in=['cpu', 'memory', 'disk'],
            timestamp__gte=since
        )
        
        result = {}
        for metric_type in ['cpu', 'memory', 'disk']:
            type_metrics = metrics.filter(metric_type=metric_type)
            if type_metrics.exists():
                result[metric_type] = {
                    'avg': type_metrics.aggregate(Avg('value'))['value__avg'],
                    'max': type_metrics.aggregate(Max('value'))['value__max'],
                    'current': type_metrics.first().value if type_metrics.first() else None,
                }
        
        return result
    
    def _get_application_metrics(self, since: datetime) -> Dict[str, Any]:
        """Get application metrics."""
        # Request statistics
        requests = PerformanceLog.objects.filter(timestamp__gte=since)
        
        total_requests = requests.count()
        error_requests = requests.filter(status_code__gte=400).count()
        
        avg_response_time = requests.aggregate(Avg('duration_ms'))['duration_ms__avg'] or 0
        
        return {
            'total_requests': total_requests,
            'error_requests': error_requests,
            'error_rate': (error_requests / total_requests * 100) if total_requests > 0 else 0,
            'avg_response_time_ms': round(avg_response_time, 2),
            'slowest_endpoints': self._get_slowest_endpoints(since, limit=5),
        }
    
    def _get_slowest_endpoints(self, since: datetime, limit: int = 5) -> List[Dict]:
        """Get slowest endpoints."""
        from django.db.models import Avg
        
        endpoints = PerformanceLog.objects.filter(
            timestamp__gte=since
        ).values('url', 'method').annotate(
            avg_time=Avg('duration_ms'),
            count=Count('id')
        ).order_by('-avg_time')[:limit]
        
        return [
            {
                'url': e['url'],
                'method': e['method'],
                'avg_time_ms': round(e['avg_time'], 2),
                'request_count': e['count'],
            }
            for e in endpoints
        ]
    
    def _get_performance_stats(self, since: datetime) -> Dict[str, Any]:
        """Get performance statistics."""
        logs = PerformanceLog.objects.filter(timestamp__gte=since)
        
        if not logs.exists():
            return {}
        
        return {
            'avg_response_time_ms': round(
                logs.aggregate(Avg('duration_ms'))['duration_ms__avg'] or 0, 2
            ),
            'max_response_time_ms': round(
                logs.aggregate(Max('duration_ms'))['duration_ms__max'] or 0, 2
            ),
            'min_response_time_ms': round(
                logs.aggregate(Min('duration_ms'))['duration_ms__min'] or 0, 2
            ),
            'avg_queries': round(
                logs.aggregate(Avg('query_count'))['query_count__avg'] or 0, 2
            ),
            'total_requests': logs.count(),
        }
    
    def _serialize_alerts(self, alerts) -> List[Dict]:
        """Serialize alerts."""
        return [
            {
                'id': alert.id,
                'title': alert.title,
                'severity': alert.severity,
                'status': alert.status,
                'created_at': alert.created_at.isoformat(),
            }
            for alert in alerts
        ]
    
    def _serialize_events(self, events) -> List[Dict]:
        """Serialize events."""
        return [
            {
                'id': event.id,
                'type': event.event_type,
                'description': event.description,
                'created_at': event.created_at.isoformat(),
            }
            for event in events
        ]


class MetricsView(APIView):
    """
    Metrics API endpoint.
    
    GET /api/monitoring/metrics/
    POST /api/monitoring/metrics/
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get metrics with filtering."""
        metric_type = request.query_params.get('type')
        hours = int(request.query_params.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        
        metrics = Metric.objects.filter(timestamp__gte=since)
        
        if metric_type:
            metrics = metrics.filter(metric_type=metric_type)
        
        # Group by time buckets
        data = list(metrics.values())
        
        return Response({
            'count': len(data),
            'data': data,
        })
    
    def post(self, request):
        """Create a new metric (for external monitoring tools)."""
        metric = Metric.objects.create(
            name=request.data.get('name'),
            metric_type=request.data.get('type'),
            value=request.data.get('value'),
            unit=request.data.get('unit', ''),
            metadata=request.data.get('metadata', {}),
        )
        
        return Response({
            'id': metric.id,
            'created': True,
        }, status=status.HTTP_201_CREATED)


class AlertsView(APIView):
    """
    Alerts API endpoint.
    
    GET /api/monitoring/alerts/
    PATCH /api/monitoring/alerts/<id>/
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get alerts with filtering."""
        status_filter = request.query_params.get('status')
        severity = request.query_params.get('severity')
        
        alerts = Alert.objects.all()
        
        if status_filter:
            alerts = alerts.filter(status=status_filter)
        if severity:
            alerts = alerts.filter(severity=severity)
        
        return Response({
            'count': alerts.count(),
            'alerts': [
                {
                    'id': a.id,
                    'title': a.title,
                    'description': a.description,
                    'severity': a.severity,
                    'status': a.status,
                    'created_at': a.created_at.isoformat(),
                }
                for a in alerts.order_by('-created_at')[:50]
            ],
        })
    
    def patch(self, request, alert_id=None):
        """Update alert status."""
        if not alert_id:
            return Response({'error': 'Alert ID required'}, status=400)
        
        try:
            alert = Alert.objects.get(id=alert_id)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=404)
        
        new_status = request.data.get('status')
        if new_status in ['acknowledged', 'resolved']:
            alert.status = new_status
            if new_status == 'resolved':
                alert.resolved_at = timezone.now()
            if new_status == 'acknowledged':
                alert.acknowledged_by = request.user
            alert.save()
        
        return Response({'status': 'updated'})


class PerformanceView(APIView):
    """
    Performance metrics API.
    
    GET /api/monitoring/performance/
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get performance metrics."""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        logs = PerformanceLog.objects.filter(timestamp__gte=since)
        
        # Group by endpoint
        endpoint_stats = logs.values('url', 'method').annotate(
            count=Count('id'),
            avg_time=Avg('duration_ms'),
            max_time=Max('duration_ms'),
        ).order_by('-count')[:20]
        
        # Time series data (hourly buckets)
        time_series = []
        for hour in range(hours):
            hour_start = since + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_logs = logs.filter(timestamp__gte=hour_start, timestamp__lt=hour_end)
            if hour_logs.exists():
                time_series.append({
                    'timestamp': hour_start.isoformat(),
                    'request_count': hour_logs.count(),
                    'avg_response_time': round(
                        hour_logs.aggregate(Avg('duration_ms'))['duration_ms__avg'] or 0, 2
                    ),
                    'error_count': hour_logs.filter(status_code__gte=400).count(),
                })
        
        return Response({
            'summary': {
                'total_requests': logs.count(),
                'avg_response_time_ms': round(
                    logs.aggregate(Avg('duration_ms'))['duration_ms__avg'] or 0, 2
                ),
                'error_rate': (
                    logs.filter(status_code__gte=400).count() / logs.count() * 100
                    if logs.count() > 0 else 0
                ),
            },
            'endpoints': list(endpoint_stats),
            'time_series': time_series,
        })


class EventsView(APIView):
    """
    System events API.
    
    GET /api/monitoring/events/
    POST /api/monitoring/events/
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get system events."""
        event_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 50))
        
        events = SystemEvent.objects.all()
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        return Response({
            'events': [
                {
                    'id': e.id,
                    'type': e.event_type,
                    'description': e.description,
                    'metadata': e.metadata,
                    'created_at': e.created_at.isoformat(),
                    'created_by': e.created_by.username if e.created_by else None,
                }
                for e in events.order_by('-created_at')[:limit]
            ],
        })
    
    def post(self, request):
        """Create a system event."""
        event = SystemEvent.objects.create(
            event_type=request.data.get('event_type'),
            description=request.data.get('description'),
            metadata=request.data.get('metadata', {}),
            created_by=request.user if request.user.is_authenticated else None,
        )
        
        return Response({
            'id': event.id,
            'created': True,
        }, status=status.HTTP_201_CREATED)
