import apiClient from './api';
import type { 
  Province, 
  District, 
  Municipality, 
  Barangay,
  LocationFilters 
} from '@/types';

export const locationsService = {
  async getProvinces(): Promise<Province[]> {
    const response = await apiClient.get<Province[]>('provinces/');
    return response.data;
  },

  async getDistricts(filters?: LocationFilters): Promise<District[]> {
    const response = await apiClient.get<District[]>('districts/', { params: filters });
    return response.data;
  },

  async getMunicipalities(filters?: LocationFilters): Promise<Municipality[]> {
    const response = await apiClient.get<Municipality[]>('municipalities/', { params: filters });
    return response.data;
  },

  async getBarangays(filters?: { municipality?: number }): Promise<Barangay[]> {
    const response = await apiClient.get<Barangay[]>('barangays/', { params: filters });
    return response.data;
  },
};
