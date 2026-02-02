import { useQuery } from '@tanstack/react-query';
import { geoService, type MapBounds } from '@/services/geo';
import { useState, useCallback } from 'react';

const MAP_DATA_QUERY_KEY = 'mapData';

interface UseMapOptions {
  bounds?: MapBounds;
  filters?: { status?: string; project_type?: number };
  enabled?: boolean;
}

export function useMapData(options: UseMapOptions = {}) {
  const { bounds, filters, enabled = true } = options;
  
  return useQuery({
    queryKey: [MAP_DATA_QUERY_KEY, bounds, filters],
    queryFn: () => geoService.getMapData(bounds, filters),
    enabled: enabled && !!bounds,
    staleTime: 30 * 1000,
  });
}

export function useNearbyProjects(lat: number, lng: number, radius = 5000) {
  return useQuery({
    queryKey: [MAP_DATA_QUERY_KEY, 'nearby', lat, lng, radius],
    queryFn: () => geoService.getNearbyProjects(lat, lng, radius),
    enabled: !!lat && !!lng,
  });
}

interface ViewportState {
  latitude: number;
  longitude: number;
  zoom: number;
}

export function useViewport(initialState: ViewportState) {
  const [viewport, setViewportState] = useState<ViewportState>(initialState);

  const setViewport = useCallback((newViewport: Partial<ViewportState>) => {
    setViewportState((prev) => ({ ...prev, ...newViewport }));
  }, []);

  const resetViewport = useCallback(() => {
    setViewportState(initialState);
  }, [initialState]);

  const getBounds = useCallback((): MapBounds | undefined => {
    const latDiff = 180 / Math.pow(2, viewport.zoom);
    const lngDiff = 360 / Math.pow(2, viewport.zoom);
    
    return {
      north: viewport.latitude + latDiff / 2,
      south: viewport.latitude - latDiff / 2,
      east: viewport.longitude + lngDiff / 2,
      west: viewport.longitude - lngDiff / 2,
    };
  }, [viewport]);

  return {
    viewport,
    setViewport,
    resetViewport,
    getBounds,
  };
}
