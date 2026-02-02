import { BarChart3, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusChart } from '@/components/dashboard/StatusChart'
import { TypeChart } from '@/components/dashboard/TypeChart'

export function ReportsPage() {
  const mockStatusData = {
    pending: 10,
    in_progress: 25,
    done: 40,
    cancelled: 5,
    on_hold: 8,
  }

  const mockTypeData = {
    Infrastructure: 30,
    Development: 25,
    Maintenance: 20,
    Research: 13,
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">
            View project statistics and analytics
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Status Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusChart data={mockStatusData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Projects by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TypeChart data={mockTypeData} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
