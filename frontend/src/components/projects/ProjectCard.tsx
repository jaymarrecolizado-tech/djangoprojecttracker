import { Link } from 'react-router-dom'
import { MapPin, Calendar } from 'lucide-react'
import { ProjectSiteListItem } from '@/types'
import { formatDate, snakeToTitleCase } from '@/lib/formatters'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface ProjectCardProps {
  project: ProjectSiteListItem
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-green-500',
  cancelled: 'bg-red-500',
  on_hold: 'bg-gray-500',
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link to={`/projects/${project.id}`}>
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{project.site_code}</p>
              <h3 className="font-semibold">{project.site_name}</h3>
            </div>
            <Badge className={statusColors[project.status] || 'bg-gray-500'}>
              {snakeToTitleCase(project.status)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span>
              {project.barangay_name}, {project.municipality_name}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{formatDate(project.created_at)}</span>
          </div>
          <div className="pt-2">
            <span className="text-xs font-medium px-2 py-1 bg-secondary rounded-full">
              {project.project_type_name}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
