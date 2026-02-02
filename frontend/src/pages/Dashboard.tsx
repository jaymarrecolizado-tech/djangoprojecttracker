import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Plus, ArrowRight } from 'lucide-react'
import { useProjects } from '@/hooks/useProjects'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { RecentProjects } from '@/components/dashboard/RecentProjects'
import { StatusChart } from '@/components/dashboard/StatusChart'
import { TypeChart } from '@/components/dashboard/TypeChart'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function Dashboard() {
  const { data: projectsData, isLoading } = useProjects({ page_size: 5 })

  const stats = useMemo(() => {
    if (!projectsData?.results) {
      return { total: 0, active: 0, completed: 0, pending: 0 }
    }

    const projects = projectsData.results
    return {
      total: projects.length,
      active: projects.filter((p) => p.status === 'in_progress').length,
      completed: projects.filter((p) => p.status === 'done').length,
      pending: projects.filter((p) => p.status === 'pending').length,
    }
  }, [projectsData])

  const statusData = useMemo(() => {
    if (!projectsData?.results) return {}
    return projectsData.results.reduce((acc, p) => {
      acc[p.status] = (acc[p.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [projectsData])

  const typeData = useMemo(() => {
    if (!projectsData?.results) return {}
    return projectsData.results.reduce((acc, p) => {
      acc[p.project_type_name] = (acc[p.project_type_name] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [projectsData])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's an overview of your projects.
          </p>
        </div>
        <Button asChild>
          <Link to="/projects/create">
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Link>
        </Button>
      </div>

      <StatsCards stats={stats} />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : (
              <StatusChart data={statusData} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects by Type</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : (
              <TypeChart data={typeData} />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Projects</CardTitle>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              View all
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          <RecentProjects
            projects={projectsData?.results || []}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>
    </div>
  )
}
