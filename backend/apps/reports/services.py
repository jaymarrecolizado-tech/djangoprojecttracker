"""Services for reports app."""
import io
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Count, Q, Sum, Avg
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from apps.projects.models import ProjectSite, ProjectType, ProjectStatus


class ReportService:
    """Service for generating reports."""
    
    def __init__(self):
        self.base_queryset = ProjectSite.objects.filter(is_deleted=False)
    
    def get_statistics(self, filters=None):
        """Get overall statistics."""
        queryset = self.base_queryset
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        total_projects = queryset.count()
        status_counts = dict(
            queryset.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        type_counts = dict(
            ProjectType.objects
            .values('name')
            .annotate(count=Count('projects', filter=Q(projects__is_deleted=False)))
            .values_list('name', 'count')
        )
        
        return {
            'total_projects': total_projects,
            'by_status': status_counts,
            'by_type': type_counts
        }
    
    def get_distribution(self, group_by='province', filters=None):
        """Get project distribution by location."""
        queryset = self.base_queryset
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        if group_by == 'province':
            distribution = dict(
                queryset.values('province__name')
                .annotate(count=Count('id'))
                .values_list('province__name', 'count')
            )
        elif group_by == 'municipality':
            distribution = dict(
                queryset.values('municipality__name')
                .annotate(count=Count('id'))
                .values_list('municipality__name', 'count')
            )
        elif group_by == 'barangay':
            distribution = dict(
                queryset.values('barangay__name')
                .annotate(count=Count('id'))
                .values_list('barangay__name', 'count')
            )
        else:
            distribution = {}
        
        return {
            'by': group_by,
            'distribution': distribution
        }
    
    def get_timeline(self, period='month', filters=None):
        """Get project timeline by date."""
        queryset = self.base_queryset
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        if period == 'day':
            timeline = list(
                queryset.annotate(period=TruncDay('created_at'))
                .values('period')
                .annotate(count=Count('id'))
                .order_by('period')
                .values('period', 'count')
            )
        elif period == 'week':
            timeline = list(
                queryset.annotate(period=TruncWeek('created_at'))
                .values('period')
                .annotate(count=Count('id'))
                .order_by('period')
                .values('period', 'count')
            )
        else:  # month
            timeline = list(
                queryset.annotate(period=TruncMonth('created_at'))
                .values('period')
                .annotate(count=Count('id'))
                .order_by('period')
                .values('period', 'count')
            )
        
        return {
            'period': period,
            'timeline': timeline
        }
    
    def get_status_report(self, filters=None):
        """Get detailed status report."""
        queryset = self.base_queryset
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        status_data = []
        for status_choice in ProjectStatus.choices:
            status_name, status_label = status_choice
            status_projects = queryset.filter(status=status_name)
            status_data.append({
                'status': status_name,
                'label': status_label,
                'count': status_projects.count(),
                'percentage': 0,  # Will be calculated after total
                'recent_projects': list(
                    status_projects.order_by('-created_at')[:5]
                    .values('site_code', 'site_name', 'created_at')
                )
            )
        
        total = sum(s['count'] for s in status_data)
        for s in status_data:
            s['percentage'] = round((s['count'] / total * 100) if total > 0 else 0, 2)
        
        return {
            'total_projects': total,
            'status_breakdown': status_data
        }
    
    def get_date_range_report(self, start_date, end_date, group_by='day', filters=None):
        """Get report for a specific date range."""
        queryset = self.base_queryset.filter(created_at__date__range=[start_date, end_date])
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        if group_by == 'day':
            data = list(
                queryset.annotate(period=TruncDay('created_at'))
                .values('period')
                .annotate(
                    count=Count('id'),
                    pending=Count('id', filter=Q(status='pending')),
                    in_progress=Count('id', filter=Q(status='in_progress')),
                    done=Count('id', filter=Q(status='done'))
                )
                .order_by('period')
            )
        elif group_by == 'week':
            data = list(
                queryset.annotate(period=TruncWeek('created_at'))
                .values('period')
                .annotate(
                    count=Count('id'),
                    pending=Count('id', filter=Q(status='pending')),
                    in_progress=Count('id', filter=Q(status='in_progress')),
                    done=Count('id', filter=Q(status='done'))
                )
                .order_by('period')
            )
        else:  # month
            data = list(
                queryset.annotate(period=TruncMonth('created_at'))
                .values('period')
                .annotate(
                    count=Count('id'),
                    pending=Count('id', filter=Q(status='pending')),
                    in_progress=Count('id', filter=Q(status='in_progress')),
                    done=Count('id', filter=Q(status='done'))
                )
                .order_by('period')
            )
        
        return {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'group_by': group_by,
            'data': data
        }
    
    def get_location_report(self, filters=None):
        """Get report grouped by location hierarchy."""
        queryset = self.base_queryset
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Province level
        province_data = list(
            queryset.values('province__name')
            .annotate(
                total=Count('id'),
                pending=Count('id', filter=Q(status='pending')),
                in_progress=Count('id', filter=Q(status='in_progress')),
                done=Count('id', filter=Q(status='done')),
                cancelled=Count('id', filter=Q(status='cancelled'))
            )
            .order_by('-total')
        )
        
        # Municipality level
        municipality_data = list(
            queryset.values('municipality__name', 'province__name')
            .annotate(
                total=Count('id'),
                pending=Count('id', filter=Q(status='pending')),
                in_progress=Count('id', filter=Q(status='in_progress')),
                done=Count('id', filter=Q(status='done'))
            )
            .order_by('-total')
        )
        
        return {
            'by_province': province_data,
            'by_municipality': municipality_data
        }
    
    def export_to_excel(self, report_type, filters=None):
        """Export report to Excel format."""
        if report_type == 'statistics':
            data = self.get_statistics(filters)
            df = pd.DataFrame([data])
        elif report_type == 'status':
            data = self.get_status_report(filters)
            df = pd.DataFrame(data['status_breakdown'])
        elif report_type == 'timeline':
            data = self.get_timeline(filters=filters)
            df = pd.DataFrame(data['timeline'])
        else:
            data = self.get_statistics(filters)
            df = pd.DataFrame([data])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=report_type.title())
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_csv(self, report_type, filters=None):
        """Export report to CSV format."""
        import csv
        
        if report_type == 'statistics':
            data = self.get_statistics(filters)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Metric', 'Value'])
            for key, value in data.items():
                if isinstance(value, dict):
                    writer.writerow([key, ''])
                    for k, v in value.items():
                        writer.writerow([f'  {k}', v])
                else:
                    writer.writerow([key, value])
        elif report_type == 'status':
            data = self.get_status_report(filters)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Status', 'Label', 'Count', 'Percentage', 'Recent Projects'])
            for item in data['status_breakdown']:
                writer.writerow([
                    item['status'], item['label'], item['count'], 
                    item['percentage'], str(item['recent_projects'])
                ])
        elif report_type == 'timeline':
            data = self.get_timeline(filters=filters)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Period', 'Count'])
            for item in data['timeline']:
                writer.writerow([item['period'], item['count']])
        else:
            data = self.get_statistics(filters)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Metric', 'Value'])
            for key, value in data.items():
                writer.writerow([key, value])
        
        return output.getvalue()
    
    def _apply_filters(self, queryset, filters):
        """Apply filters to queryset."""
        if 'status' in filters and filters['status']:
            queryset = queryset.filter(status=filters['status'])
        if 'project_type' in filters and filters['project_type']:
            queryset = queryset.filter(project_type_id=filters['project_type'])
        if 'province' in filters and filters['province']:
            queryset = queryset.filter(province_id=filters['province'])
        if 'municipality' in filters and filters['municipality']:
            queryset = queryset.filter(municipality_id=filters['municipality'])
        if 'barangay' in filters and filters['barangay']:
            queryset = queryset.filter(barangay_id=filters['barangay'])
        if 'start_date' in filters and filters['start_date']:
            queryset = queryset.filter(created_at__date__gte=filters['start_date'])
        if 'end_date' in filters and filters['end_date']:
            queryset = queryset.filter(created_at__date__lte=filters['end_date'])
        return queryset
