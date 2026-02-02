"""Views for geo app."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.db.models.functions import Distance
from apps.projects.models import ProjectSite
from apps.common.responses import success_response
from .utils import projects_to_feature_collection

class MapDataView(APIView):
    """Get projects as GeoJSON for map display."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = ProjectSite.objects.filter(is_deleted=False).select_related(
            'project_type', 'province', 'municipality'
        )
        
        # Filter by status
        status = request.query_params.get('status')
        if status:
            projects = projects.filter(status=status)
        
        # Filter by project type
        project_type = request.query_params.get('project_type')
        if project_type:
            projects = projects.filter(project_type_id=project_type)
        
        # Filter by province
        province = request.query_params.get('province')
        if province:
            projects = projects.filter(province_id=province)
        
        geojson = projects_to_feature_collection(projects)
        return success_response(data={'geojson': geojson})


class NearbyProjectsView(APIView):
    """Find projects near a point."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 5000))  # meters
        except (TypeError, ValueError):
            return success_response(data={'projects': []}, message='Invalid coordinates')
        
        point = Point(lng, lat, srid=4326)
        projects = ProjectSite.objects.filter(
            is_deleted=False
        ).annotate(
            distance=Distance('location', point)
        ).filter(distance__lte=radius).order_by('distance')[:20]
        
        data = [{
            'id': p.id,
            'site_code': p.site_code,
            'site_name': p.site_name,
            'status': p.status,
            'distance': p.distance.m if hasattr(p.distance, 'm') else 0
        } for p in projects]
        
        return success_response(data={'projects': data})


class BoundsFilterView(APIView):
    """Filter projects by map bounds."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sw_lat = float(request.query_params.get('sw_lat'))
            sw_lng = float(request.query_params.get('sw_lng'))
            ne_lat = float(request.query_params.get('ne_lat'))
            ne_lng = float(request.query_params.get('ne_lng'))
        except (TypeError, ValueError):
            return success_response(data={'projects': []}, message='Invalid bounds')
        
        bbox = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))
        projects = ProjectSite.objects.filter(
            is_deleted=False,
            location__within=bbox
        ).select_related('project_type', 'province', 'municipality')
        
        geojson = projects_to_feature_collection(projects)
        return success_response(data={'geojson': geojson})
