import { Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ProjectList } from '@/components/projects/ProjectList'
import { ProjectFilters } from '@/components/projects/ProjectFilters'
import { Button } from '@/components/ui/button'

export function ProjectsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage and view all projects in the system
          </p>
        </div>
        <Button asChild>
          <Link to="/projects/create">
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Link>
        </Button>
      </div>

      <ProjectFilters />

      <ProjectList />
    </div>
  )
}
