// Common types used throughout the application

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type UserRole = 'admin' | 'manager' | 'editor' | 'viewer';

export type ProjectStatus = 'pending' | 'in_progress' | 'done' | 'cancelled' | 'on_hold';

export interface SelectOption {
  value: string;
  label: string;
}

export interface MapViewport {
  latitude: number;
  longitude: number;
  zoom: number;
}

export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number];
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface FilterState {
  search?: string;
  status?: ProjectStatus | '';
  projectType?: number | '';
  province?: number | '';
  district?: number | '';
  municipality?: number | '';
  barangay?: number | '';
  dateFrom?: string;
  dateTo?: string;
}

export * from './auth';
export * from './project';
export * from './location';
export * from './api';
