"""GeoJSON utilities."""
from typing import List, Dict, Any

def project_to_geojson(project) -> Dict[str, Any]:
    """Convert a project to GeoJSON feature."""
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [float(project.longitude), float(project.latitude)]
        },
        'properties': {
            'id': project.id,
            'site_code': project.site_code,
            'site_name': project.site_name,
            'status': project.status,
            'status_display': project.get_status_display(),
            'status_color': project.status_color,
            'project_type': project.project_type.name if project.project_type else None,
            'province': project.province.name if project.province else None,
            'municipality': project.municipality.name if project.municipality else None,
        }
    }

def projects_to_feature_collection(projects: List) -> Dict[str, Any]:
    """Convert projects to GeoJSON FeatureCollection."""
    return {
        'type': 'FeatureCollection',
        'features': [project_to_geojson(p) for p in projects]
    }
