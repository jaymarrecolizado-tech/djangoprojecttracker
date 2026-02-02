import { MapView } from '@/components/map/MapView'
import { useMapData, useViewport } from '@/hooks/useMap'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function MapPage() {
  const { viewport, setViewport, getBounds } = useViewport({
    latitude: 14.5995,
    longitude: 120.9842,
    zoom: 12,
  })

  const bounds = getBounds()
  const { data: mapData, isLoading } = useMapData({
    bounds,
    enabled: !!bounds,
  })

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-3xl font-bold">Project Map</h1>
        <p className="text-muted-foreground">
          View all projects on an interactive map
        </p>
      </div>

      <Card className="h-full">
        <CardContent className="p-0 h-full">
          <MapView
            features={mapData?.features || []}
            center={[viewport.longitude, viewport.latitude]}
            zoom={viewport.zoom}
          />
        </CardContent>
      </Card>
    </div>
  )
}
