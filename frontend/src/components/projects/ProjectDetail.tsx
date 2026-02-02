import { MapPin, Calendar, User, FileText } from 'lucide-react'
import { ProjectSite } from '@/types'
import { formatDate, formatCoordinates, snakeToTitleCase } from '@/lib/formatters'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface ProjectDetailProps {
  project: ProjectSite
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-green-500',
  cancelled: 'bg-red-500',
  on_hold: 'bg-gray-500',
}

export function ProjectDetail({ project }: ProjectDetailProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{project.site_code}</p>
              <CardTitle className="text-2xl">{project.site_name}</CardTitle>
            </div>
            <Badge className={statusColors[project.status] || 'bg-gray-500'}>
              {snakeToTitleCase(project.status)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Project Type</p>
              <p>{project.project_type.name}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Location</p>
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>
                  {project.barangay.name}, {project.municipality.name}, {project.province.name}
                  {project.district && ` (${project.district.name})`}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Coordinates</p>
              <p>{formatCoordinates(project.latitude, project.longitude)}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Activation Date</p>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span>{project.activation_date ? formatDate(project.activation_date) : 'Not set'}</span>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Created By</p>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4" />
                <span>{project.created_by.full_name}</span>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <span>{formatDate(project.created_at)}</span>
            </div>
          </div>

          {project.remarks && (
            <div className="space-y-1 pt-4 border-t">
              <p className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Remarks
              </p>
              <p className="text-sm">{project.remarks}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
