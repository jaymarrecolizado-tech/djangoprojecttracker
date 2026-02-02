import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ProjectForm } from '@/components/projects/ProjectForm'
import { useCreateProject } from '@/hooks/useProjects'
import { ProjectFormData } from '@/lib/validators'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ProjectCreatePage() {
  const navigate = useNavigate()
  const createProject = useCreateProject()

  const handleSubmit = async (data: ProjectFormData) => {
    try {
      await createProject.mutateAsync(data)
      toast.success('Project created successfully')
      navigate('/projects')
    } catch {
      toast.error('Failed to create project')
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Create Project</h1>
        <p className="text-muted-foreground">
          Add a new project to the system
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent>
          <ProjectForm onSubmit={handleSubmit} isLoading={createProject.isPending} />
        </CardContent>
      </Card>
    </div>
  )
}
