import type { GeoJSONPoint } from './index';
import type { User } from './auth';
import type { LocationNode } from './location';

export interface ProjectType {
  id: number;
  name: string;
  code_prefix: string;
  color_code: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

export interface ProjectSite {
  id: number;
  site_code: string;
  site_name: string;
  location: GeoJSONPoint;
  latitude: number;
  longitude: number;
  status: 'pending' | 'in_progress' | 'done' | 'cancelled' | 'on_hold';
  remarks: string;
  activation_date?: string;
  metadata: Record<string, unknown>;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  project_type: ProjectType;
  province: LocationNode;
  district: LocationNode | null;
  municipality: LocationNode;
  barangay: LocationNode;
  created_by: User;
  updated_by: User;
}

export interface ProjectSiteListItem {
  id: number;
  site_code: string;
  site_name: string;
  latitude: number;
  longitude: number;
  status: ProjectSite['status'];
  project_type_name: string;
  province_name: string;
  municipality_name: string;
  barangay_name: string;
  created_at: string;
}

export interface ProjectStatusHistory {
  id: number;
  old_status: string;
  new_status: string;
  reason: string;
  changed_at: string;
  changed_by: User;
}

export interface CreateProjectData {
  site_code: string;
  site_name: string;
  latitude: number;
  longitude: number;
  status: ProjectSite['status'];
  project_type: number;
  province: number;
  district?: number | null;
  municipality: number;
  barangay: number;
  remarks?: string;
  activation_date?: string;
  metadata?: Record<string, unknown>;
}

export interface UpdateProjectData {
  site_name?: string;
  latitude?: number;
  longitude?: number;
  status?: ProjectSite['status'];
  project_type?: number;
  province?: number;
  district?: number | null;
  municipality?: number;
  barangay?: number;
  remarks?: string;
  activation_date?: string;
  metadata?: Record<string, unknown>;
}

export interface StatusChangeData {
  new_status: ProjectSite['status'];
  reason: string;
}

export interface ProjectFilters {
  search?: string;
  status?: string;
  project_type?: number;
  province?: number;
  district?: number;
  municipality?: number;
  barangay?: number;
  date_from?: string;
  date_to?: string;
  ordering?: string;
}

export interface ProjectGeoJSONFeature {
  type: 'Feature';
  geometry: GeoJSONPoint;
  properties: {
    id: number;
    site_code: string;
    site_name: string;
    status: string;
    project_type_name: string;
    province_name: string;
    municipality_name: string;
    barangay_name: string;
  };
}

export interface ProjectGeoJSONCollection {
  type: 'FeatureCollection';
  features: ProjectGeoJSONFeature[];
}
