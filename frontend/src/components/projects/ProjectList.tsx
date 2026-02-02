import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useProjects } from '@/hooks/useProjects'
import { formatDate, snakeToTitleCase } from '@/lib/formatters'
import { useFilterStore } from '@/stores/filters'
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
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
import { ProjectActions } from './ProjectActions'

interface ProjectListProps {
  onDelete?: (id: number) => void
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-green-500',
  cancelled: 'bg-red-500',
  on_hold: 'bg-gray-500',
}

export function ProjectList({ onDelete }: ProjectListProps) {
  const [page, setPage] = useState(1)
  const pageSize = 10
  const filters = useFilterStore()

  const { data, isLoading } = useProjects({
    page,
    page_size: pageSize,
    search: filters.search,
    status: filters.status || undefined,
    project_type: filters.project_type,
    province: filters.province,
    municipality: filters.municipality,
    barangay: filters.barangay,
    date_from: filters.date_from,
    date_to: filters.date_to,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  const projects = data?.results || []
  const totalPages = Math.ceil((data?.count || 0) / pageSize)

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Site Code</TableHead>
              <TableHead>Site Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {projects.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No projects found
                </TableCell>
              </TableRow>
            ) : (
              projects.map((project) => (
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
                  <TableCell>{project.project_type_name}</TableCell>
                  <TableCell>
                    <Badge className={statusColors[project.status] || 'bg-gray-500'}>
                      {snakeToTitleCase(project.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {project.municipality_name}, {project.province_name}
                  </TableCell>
                  <TableCell>{formatDate(project.created_at)}</TableCell>
                  <TableCell className="text-right">
                    <ProjectActions
                      projectId={project.id}
                      onDelete={onDelete}
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className={page === 1 ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
              <PaginationItem key={pageNum}>
                <PaginationLink
                  onClick={() => setPage(pageNum)}
                  isActive={page === pageNum}
                >
                  {pageNum}
                </PaginationLink>
              </PaginationItem>
            ))}
            <PaginationItem>
              <PaginationNext
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className={page === totalPages ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  )
}
