"""Views for reports app."""
import io
from django.http import HttpResponse
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.projects.models import ProjectSite, ProjectType, ProjectStatus
from apps.common.responses import success_response
from .services import ReportService


class StatisticsView(APIView):
    """Get overall statistics."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_statistics(filters)
        return success_response(data={'statistics': data})


class DistributionView(APIView):
    """Get project distribution by location."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_by = request.query_params.get('group_by', 'province')
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_distribution(group_by=group_by, filters=filters)
        return success_response(data={'distribution': data})


class TimelineView(APIView):
    """Get project timeline."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'month')
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_timeline(period=period, filters=filters)
        return success_response(data={'timeline': data})


class StatusReportView(APIView):
    """Get detailed status report."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_status_report(filters=filters)
        return success_response(data={'status_report': data})


class DateRangeReportView(APIView):
    """Get report for a specific date range."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')
        
        if not start_date or not end_date:
            return success_response(
                data={'error': 'start_date and end_date are required'},
                message='Please provide start_date and end_date parameters'
            )
        
        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
        except ValueError:
            return success_response(
                data={'error': 'Invalid date format'},
                message='Dates must be in YYYY-MM-DD format'
            )
        
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_date_range_report(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            filters=filters
        )
        return success_response(data={'date_range_report': data})


class LocationReportView(APIView):
    """Get report grouped by location."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = ReportService()
        filters = self._get_filters(request)
        data = service.get_location_report(filters=filters)
        return success_response(data={'location_report': data})


class ExportReportView(APIView):
    """Export report to CSV or Excel."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        report_type = request.query_params.get('type', 'statistics')
        format_type = request.query_params.get('format', 'csv').lower()
        
        service = ReportService()
        filters = self._get_filters(request)
        
        if format_type == 'excel':
            content = service.export_to_excel(report_type, filters)
            response = HttpResponse(
                content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        else:
            content = service.export_to_csv(report_type, filters)
            response = HttpResponse(content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        
        return response

    def _get_filters(self, request):
        """Extract filters from request query params."""
        filters = {}
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        if request.query_params.get('project_type'):
            filters['project_type'] = request.query_params.get('project_type')
        if request.query_params.get('province'):
            filters['province'] = request.query_params.get('province')
        if request.query_params.get('municipality'):
            filters['municipality'] = request.query_params.get('municipality')
        if request.query_params.get('barangay'):
            filters['barangay'] = request.query_params.get('barangay')
        return filters
