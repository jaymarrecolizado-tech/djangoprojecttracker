import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ProjectForm } from '@/components/projects/ProjectForm'
import { useProject, useUpdateProject } from '@/hooks/useProjects'
import { ProjectFormData } from '@/lib/validators'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function ProjectEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const projectId = parseInt(id || '0')

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
      <div className="space-y-6 max-w-4xl">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Edit Project</h1>
        <p className="text-muted-foreground">
          Update project details
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent>
          {project && (
            <ProjectForm
              project={project}
              onSubmit={handleSubmit}
              isLoading={updateProject.isPending}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
