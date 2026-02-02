"""Views for reports app."""
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.projects.models import ProjectSite, ProjectType, ProjectStatus
from apps.common.responses import success_response

class StatisticsView(APIView):
    """Get overall statistics."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_projects = ProjectSite.objects.filter(is_deleted=False).count()
        status_counts = dict(ProjectSite.objects.filter(is_deleted=False).values('status').annotate(count=Count('id')).values_list('status', 'count'))
        type_counts = dict(ProjectType.objects.values('name').annotate(count=Count('projects', filter=Q(projects__is_deleted=False))).values_list('name', 'count'))

        return success_response(data={
            'statistics': {
                'total_projects': total_projects,
                'by_status': status_counts,
                'by_type': type_counts
            }
        })


class DistributionView(APIView):
    """Get project distribution by location."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        province_dist = dict(ProjectSite.objects.filter(is_deleted=False).values('province__name').annotate(count=Count('id')).values_list('province__name', 'count'))
        
        return success_response(data={
            'distribution': {
                'by_province': province_dist
            }
        })


class TimelineView(APIView):
    """Get project timeline."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncMonth
        
        timeline = list(ProjectSite.objects.filter(is_deleted=False).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month').values('month', 'count'))
        
        return success_response(data={'timeline': timeline})
