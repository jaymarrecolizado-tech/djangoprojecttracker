import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Edit, Trash2, ArrowLeft } from 'lucide-react'
import { useProject, useProjectHistory, useDeleteProject, useChangeStatus } from '@/hooks/useProjects'
import { useAuth } from '@/hooks/useAuth'
import { ProjectDetail } from '@/components/projects/ProjectDetail'
import { StatusHistory } from '@/components/projects/StatusHistory'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useState } from 'react'

const statusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'on_hold', label: 'On Hold' },
]

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const projectId = id ? parseInt(id) : 0
  const { currentUser } = useAuth()
  
  const { data: project, isLoading: projectLoading } = useProject(projectId)
  const { data: history, isLoading: historyLoading } = useProjectHistory(projectId)
  const deleteProject = useDeleteProject()
  const changeStatus = useChangeStatus()
  
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isStatusDialogOpen, setIsStatusDialogOpen] = useState(false)
  const [newStatus, setNewStatus] = useState<string>('')
  const [statusReason, setStatusReason] = useState('')

  const handleDelete = async () => {
    try {
      await deleteProject.mutateAsync(projectId)
      toast.success('Project deleted successfully')
      navigate('/projects')
    } catch {
      toast.error('Failed to delete project')
    }
  }

  const handleStatusChange = async () => {
    if (!newStatus) return
    try {
      await changeStatus.mutateAsync({
        id: projectId,
        data: { new_status: newStatus as any, reason: statusReason }
      })
      toast.success('Status updated successfully')
      setIsStatusDialogOpen(false)
      setNewStatus('')
      setStatusReason('')
    } catch {
      toast.error('Failed to update status')
    }
  }

  if (projectLoading) {
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/projects')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Project Details</h1>
            <p className="text-muted-foreground">
              View and manage project information
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsStatusDialogOpen(true)}>
            Update Status
          </Button>
          <Button asChild>
            <Link to={`/projects/${projectId}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          {(currentUser?.role === 'admin' || currentUser?.role === 'manager' || project.created_by.id === currentUser?.id) && (
            <Button variant="destructive" onClick={() => setIsDeleteDialogOpen(true)}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ProjectDetail project={project} />
        </div>
        <div>
          <StatusHistory history={history || []} />
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Project</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this project? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDelete}
              disabled={deleteProject.isPending}
            >
              {deleteProject.isPending ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Status Change Dialog */}
      <Dialog open={isStatusDialogOpen} onOpenChange={setIsStatusDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Status</DialogTitle>
            <DialogDescription>
              Change the project status and provide a reason.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="status">New Status</Label>
              <Select value={newStatus} onValueChange={setNewStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((s) => (
                    <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Reason</Label>
              <Textarea
                id="reason"
                placeholder="Enter reason for status change"
                value={statusReason}
                onChange={(e) => setStatusReason(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsStatusDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleStatusChange}
              disabled={!newStatus || !statusReason || changeStatus.isPending}
            >
              {changeStatus.isPending ? 'Updating...' : 'Update Status'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

import { Link } from 'react-router-dom'
