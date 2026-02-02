import type { GeoJSONPoint } from './index';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Geometry = Record<string, any>;

export interface LocationNode {
  id: number;
  name: string;
  code: string;
}

export interface Province extends LocationNode {
  centroid: GeoJSONPoint | null;
  boundary: Geometry | null;
}

export interface District extends LocationNode {
  province: number;
  province_name: string;
  centroid: GeoJSONPoint | null;
  boundary: Geometry | null;
}

export interface Municipality extends LocationNode {
  province: number;
  province_name: string;
  district: number | null;
  district_name: string | null;
  centroid: GeoJSONPoint | null;
  boundary: Geometry | null;
}

export interface Barangay extends LocationNode {
  municipality: number;
  municipality_name: string;
  centroid: GeoJSONPoint | null;
  boundary: Geometry | null;
}

export interface LocationHierarchy {
  provinces: Province[];
  districts: District[];
  municipalities: Municipality[];
  barangays: Barangay[];
}

export interface LocationFilters {
  province?: number;
  district?: number;
  municipality?: number;
}
