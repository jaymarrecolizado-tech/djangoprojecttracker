import { useMemo } from 'react'
import { Download, Calendar, Filter } from 'lucide-react'
import { useProjects } from '@/hooks/useProjects'
import { StatusChart } from '@/components/dashboard/StatusChart'
import { TypeChart } from '@/components/dashboard/TypeChart'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useState } from 'react'

export function ReportsPage() {
  const [dateRange, setDateRange] = useState('all')
  const { data: projectsData, isLoading } = useProjects({ page_size: 1000 })

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
      on_hold: projects.filter((p) => p.status === 'on_hold').length,
      cancelled: projects.filter((p) => p.status === 'cancelled').length,
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

  const handleExport = () => {
    // Generate CSV export
    const headers = ['Site Code', 'Site Name', 'Type', 'Status', 'Province', 'Municipality', 'Barangay', 'Created At']
    const rows = projectsData?.results.map((p) => [
      p.site_code,
      p.site_name,
      p.project_type_name,
      p.status,
      p.province_name,
      p.municipality_name,
      p.barangay_name,
      p.created_at,
    ]) || []

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `projects_report_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">
            Analytics and insights for your projects
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Date Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="year">This Year</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <Skeleton className="h-96 w-full" />
            <Skeleton className="h-96 w-full" />
          </div>
        </div>
      ) : (
        <>
          <StatsCards stats={stats} />

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Status Distribution</CardTitle>
                <CardDescription>
                  Projects grouped by current status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StatusChart data={statusData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Projects by Type</CardTitle>
                <CardDescription>
                  Distribution of project types
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TypeChart data={typeData} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Summary Statistics</CardTitle>
              <CardDescription>
                Key metrics for your projects
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-3">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Completion Rate</p>
                  <p className="text-3xl font-bold">
                    {stats.total > 0
                      ? ((stats.completed / stats.total) * 100).toFixed(1)
                      : 0}
                    %
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Active Projects</p>
                  <p className="text-3xl font-bold">{stats.active}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Pending Rate</p>
                  <p className="text-3xl font-bold">
                    {stats.total > 0
                      ? ((stats.pending / stats.total) * 100).toFixed(1)
                      : 0}
                    %
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
