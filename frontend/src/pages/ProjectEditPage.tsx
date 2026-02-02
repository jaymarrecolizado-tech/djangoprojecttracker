import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ArrowLeft } from 'lucide-react'
import { useProject, useUpdateProject } from '@/hooks/useProjects'
import { ProjectForm } from '@/components/projects/ProjectForm'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ProjectFormData } from '@/lib/validators'

export function ProjectEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const projectId = id ? parseInt(id) : 0

  const { data: project, isLoading } = useProject(projectId)
  const updateProject = useUpdateProject()

  const handleSubmit = async (data: ProjectFormData) => {
    try {
      await updateProject.mutateAsync({ id: projectId, data })
      toast.success('Project updated successfully')
      navigate(`/projects/${projectId}`)
    } catch {
      toast.error('Failed to update project')
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h2 className="text-2xl font-bold">Project not found</h2>
        <Button variant="outline" onClick={() => navigate('/projects')} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Projects
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(`/projects/${projectId}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Project</h1>
          <p className="text-muted-foreground">
            Update project information
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent>
          <ProjectForm
            project={project}
            onSubmit={handleSubmit}
            isLoading={updateProject.isPending}
          />
        </CardContent>
      </Card>
    </div>
  )
}
