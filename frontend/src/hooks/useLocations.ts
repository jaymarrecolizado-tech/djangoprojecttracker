import { useQuery } from '@tanstack/react-query';
import { locationsService } from '@/services/locations';
import { projectTypesService } from '@/services/projects';
import type { LocationFilters } from '@/types';

const LOCATIONS_QUERY_KEY = 'locations';
const PROJECT_TYPES_QUERY_KEY = 'projectTypes';

export function useProvinces() {
  return useQuery({
    queryKey: [LOCATIONS_QUERY_KEY, 'provinces'],
    queryFn: () => locationsService.getProvinces(),
    staleTime: 60 * 60 * 1000,
  });
}

export function useDistricts(filters?: LocationFilters) {
  return useQuery({
    queryKey: [LOCATIONS_QUERY_KEY, 'districts', filters],
    queryFn: () => locationsService.getDistricts(filters),
    enabled: !!filters?.province,
    staleTime: 30 * 60 * 1000,
  });
}

export function useMunicipalities(filters?: LocationFilters) {
  return useQuery({
    queryKey: [LOCATIONS_QUERY_KEY, 'municipalities', filters],
    queryFn: () => locationsService.getMunicipalities(filters),
    enabled: !!filters?.province,
    staleTime: 30 * 60 * 1000,
  });
}

export function useBarangays(municipalityId?: number) {
  return useQuery({
    queryKey: [LOCATIONS_QUERY_KEY, 'barangays', municipalityId],
    queryFn: () => locationsService.getBarangays({ municipality: municipalityId }),
    enabled: !!municipalityId,
    staleTime: 30 * 60 * 1000,
  });
}

export function useProjectTypes() {
  return useQuery({
    queryKey: [PROJECT_TYPES_QUERY_KEY],
    queryFn: () => projectTypesService.getProjectTypes(),
    staleTime: 60 * 60 * 1000,
  });
}
