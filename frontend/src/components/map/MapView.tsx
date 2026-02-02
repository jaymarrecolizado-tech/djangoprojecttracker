import { useRef, useEffect, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { ProjectGeoJSONFeature } from '@/types'
import { ProjectPopup } from './ProjectPopup'

interface MapViewProps {
  features: ProjectGeoJSONFeature[]
  center?: [number, number]
  zoom?: number
  onFeatureClick?: (feature: ProjectGeoJSONFeature) => void
}

export function MapView({ features, center = [120.9842, 14.5995], zoom = 12, onFeatureClick }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const [selectedFeature, setSelectedFeature] = useState<ProjectGeoJSONFeature | null>(null)
  const [popupPosition, setPopupPosition] = useState<{ x: number; y: number } | null>(null)

  useEffect(() => {
    if (!mapContainer.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: center,
      zoom: zoom,
    })

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right')
    map.current.addControl(new maplibregl.FullscreenControl(), 'top-right')

    return () => {
      map.current?.remove()
    }
  }, [])

  useEffect(() => {
    if (!map.current) return

    const source = map.current.getSource('projects') as maplibregl.GeoJSONSource
    if (source) {
      source.setData({
        type: 'FeatureCollection',
        features: features as GeoJSON.Feature[],
      })
    } else {
      map.current.on('load', () => {
        if (!map.current) return

        map.current.addSource('projects', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: features as GeoJSON.Feature[],
          },
        })

        map.current.addLayer({
          id: 'projects-circle',
          type: 'circle',
          source: 'projects',
          paint: {
            'circle-radius': 8,
            'circle-color': '#3B82F6',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#fff',
          },
        })

        map.current.on('click', 'projects-circle', (e) => {
          if (e.features && e.features[0]) {
            const feature = e.features[0] as unknown as ProjectGeoJSONFeature
            setSelectedFeature(feature)
            setPopupPosition({ x: e.point.x, y: e.point.y })
            onFeatureClick?.(feature)
          }
        })

        map.current.on('mouseenter', 'projects-circle', () => {
          if (map.current) map.current.getCanvas().style.cursor = 'pointer'
        })

        map.current.on('mouseleave', 'projects-circle', () => {
          if (map.current) map.current.getCanvas().style.cursor = ''
        })
      })
    }
  }, [features])

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full min-h-[400px]" />
      {selectedFeature && popupPosition && (
        <ProjectPopup
          feature={selectedFeature}
          position={popupPosition}
          onClose={() => {
            setSelectedFeature(null)
            setPopupPosition(null)
          }}
        />
      )}
    </div>
  )
}
