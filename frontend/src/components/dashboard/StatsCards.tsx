import { FolderKanban, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface StatsCardsProps {
  stats: {
    total: number
    active: number
    completed: number
    pending: number
  }
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: 'Total Projects',
      value: stats.total,
      icon: FolderKanban,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Active Projects',
      value: stats.active,
      icon: Clock,
      color: 'text-green-500',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Completed',
      value: stats.completed,
      icon: CheckCircle2,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Pending',
      value: stats.pending,
      icon: AlertCircle,
      color: 'text-amber-500',
      bgColor: 'bg-amber-100',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            <div className={`rounded-full p-2 ${card.bgColor}`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
