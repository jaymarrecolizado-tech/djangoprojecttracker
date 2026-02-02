import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Pencil } from 'lucide-react'
import { useProject, useProjectHistory } from '@/hooks/useProjects'
import { ProjectDetail } from '@/components/projects/ProjectDetail'
import { StatusHistory } from '@/components/projects/StatusHistory'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = parseInt(id || '0')

  const { data: project, isLoading: isLoadingProject } = useProject(projectId)
  const { data: history, isLoading: isLoadingHistory } = useProjectHistory(projectId)

  if (isLoadingProject) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Project not found</h2>
        <Button asChild className="mt-4">
          <Link to="/projects">Back to Projects</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" asChild>
          <Link to="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
        <Button asChild>
          <Link to={`/projects/${projectId}/edit`}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit Project
          </Link>
        </Button>
      </div>

      <Tabs defaultValue="details">
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="history">Status History</TabsTrigger>
        </TabsList>
        <TabsContent value="details" className="space-y-6">
          <ProjectDetail project={project} />
        </TabsContent>
        <TabsContent value="history">
          {isLoadingHistory ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <StatusHistory history={history || []} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
