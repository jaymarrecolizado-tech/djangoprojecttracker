import apiClient from './api';
import type { 
  ProjectGeoJSONCollection,
  ProjectGeoJSONFeature
} from '@/types';

export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface NearbyProject {
  id: number;
  site_code: string;
  site_name: string;
  status: string;
  project_type_name: string;
  province_name: string;
  municipality_name: string;
  barangay_name: string;
  latitude: number;
  longitude: number;
  distance: number;
}

export const geoService = {
  async getMapData(
    bounds?: MapBounds, 
    filters?: { status?: string; project_type?: number }
  ): Promise<ProjectGeoJSONCollection> {
    const params: Record<string, unknown> = { ...filters };
    if (bounds) {
      params.bbox = `${bounds.west},${bounds.south},${bounds.east},${bounds.north}`;
    }
    const response = await apiClient.get<ProjectGeoJSONCollection>('projects/geojson/', { params });
    return response.data;
  },

  async getNearbyProjects(lat: number, lng: number, radius = 5000): Promise<NearbyProject[]> {
    const response = await apiClient.get<NearbyProject[]>('projects/nearby/', {
      params: { lat, lng, radius }
    });
    return response.data;
  },
};
