import { X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ProjectGeoJSONFeature } from '@/types'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { snakeToTitleCase } from '@/lib/formatters'

interface ProjectPopupProps {
  feature: ProjectGeoJSONFeature
  position: { x: number; y: number }
  onClose: () => void
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-green-500',
  cancelled: 'bg-red-500',
  on_hold: 'bg-gray-500',
}

export function ProjectPopup({ feature, position, onClose }: ProjectPopupProps) {
  const { properties } = feature

  return (
    <Card
      className="absolute z-10 w-64 shadow-lg"
      style={{ left: position.x + 10, top: position.y - 10 }}
    >
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div>
          <p className="text-xs text-muted-foreground">{properties.site_code}</p>
          <h4 className="font-semibold text-sm">{properties.site_name}</h4>
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6 -mt-2 -mr-2" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        <Badge className={statusColors[properties.status] || 'bg-gray-500'}>
          {snakeToTitleCase(properties.status)}
        </Badge>
        <p className="text-xs text-muted-foreground">
          {properties.barangay_name}, {properties.municipality_name}
        </p>
        <p className="text-xs font-medium">{properties.project_type_name}</p>
        <Button asChild size="sm" className="w-full mt-2">
          <Link to={`/projects/${properties.id}`}>View Details</Link>
        </Button>
      </CardContent>
    </Card>
  )
}
