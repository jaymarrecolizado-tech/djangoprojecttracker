import { Clock, ArrowRight } from 'lucide-react'
import { ProjectStatusHistory } from '@/types'
import { formatDateTime, snakeToTitleCase } from '@/lib/formatters'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface StatusHistoryProps {
  history: ProjectStatusHistory[]
}

export function StatusHistory({ history }: StatusHistoryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Status History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-4">
          <div className="absolute left-2 top-2 bottom-2 w-px bg-border" />
          
          {history.map((item, index) => (
            <div key={item.id} className="relative flex gap-4 pl-6">
              <div className="absolute left-0 top-1 h-4 w-4 rounded-full border-2 border-primary bg-background" />
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium">
                    {snakeToTitleCase(item.old_status)}
                  </span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-primary">
                    {snakeToTitleCase(item.new_status)}
                  </span>
                </div>
                
                {item.reason && (
                  <p className="text-sm text-muted-foreground">
                    Reason: {item.reason}
                  </p>
                )}
                
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>By {item.changed_by.full_name}</span>
                  <span>•</span>
                  <span>{formatDateTime(item.changed_at)}</span>
                </div>
              </div>
            </div>
          ))}
          
          {history.length === 0 && (
            <p className="text-sm text-muted-foreground pl-6">
              No status changes recorded yet.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
