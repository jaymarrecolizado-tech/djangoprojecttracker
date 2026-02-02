import { Link } from 'react-router-dom'
import { formatDate, snakeToTitleCase } from '@/lib/formatters'
import { ProjectSiteListItem } from '@/types'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

interface RecentProjectsProps {
  projects: ProjectSiteListItem[]
  isLoading: boolean
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-green-500',
  cancelled: 'bg-red-500',
  on_hold: 'bg-gray-500',
}

export function RecentProjects({ projects, isLoading }: RecentProjectsProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Site Code</TableHead>
          <TableHead>Site Name</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Location</TableHead>
          <TableHead>Created</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {projects.map((project) => (
          <TableRow key={project.id}>
            <TableCell>
              <Link
                to={`/projects/${project.id}`}
                className="font-medium hover:underline"
              >
                {project.site_code}
              </Link>
            </TableCell>
            <TableCell>{project.site_name}</TableCell>
            <TableCell>
              <Badge className={statusColors[project.status] || 'bg-gray-500'}>
                {snakeToTitleCase(project.status)}
              </Badge>
            </TableCell>
            <TableCell>
              {project.municipality_name}, {project.province_name}
            </TableCell>
            <TableCell>{formatDate(project.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
