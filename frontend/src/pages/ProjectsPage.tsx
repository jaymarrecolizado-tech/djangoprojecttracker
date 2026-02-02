import { Link } from 'react-router-dom'
import { Plus, LayoutGrid, List } from 'lucide-react'
import { useState } from 'react'
import { ProjectList } from '@/components/projects/ProjectList'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { ProjectFilters } from '@/components/projects/ProjectFilters'
import { Button } from '@/components/ui/button'
import { useProjects, useDeleteProject } from '@/hooks/useProjects'
import { useFilterStore } from '@/stores/filters'

export function ProjectsPage() {
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list')
  const filters = useFilterStore()
  const deleteProject = useDeleteProject()

  const { data: projectsData } = useProjects({
    search: filters.search,
    status: filters.status,
    project_type: filters.project_type,
    province: filters.province,
    municipality: filters.municipality,
    barangay: filters.barangay,
    date_from: filters.date_from,
    date_to: filters.date_to,
  })

  const handleDelete = async (id: number) => {
    await deleteProject.mutateAsync(id)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage and track all your projects
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('grid')}
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button asChild>
            <Link to="/projects/create">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>
        </div>
      </div>

      <ProjectFilters />

      {viewMode === 'list' ? (
        <ProjectList onDelete={handleDelete} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projectsData?.results.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  )
}
