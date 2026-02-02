import { useAuthStore } from '@/stores/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/formatters'

export function UserProfilePage() {
  const { user } = useAuthStore()

  if (!user) return null

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold">User Profile</h1>
        <p className="text-muted-foreground">
          View and manage your profile information
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center gap-4">
          <Avatar className="h-20 w-20">
            <AvatarFallback className="text-2xl">{getInitials(user.full_name)}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle>{user.full_name}</CardTitle>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            <Badge className="mt-2" variant="outline">{user.role}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Username</p>
              <p>{user.username}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Email</p>
              <p>{user.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Role</p>
              <p className="capitalize">{user.role}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <p>{user.is_active ? 'Active' : 'Inactive'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Joined</p>
              <p>{formatDate(user.created_at)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Last Login</p>
              <p>{user.last_login ? formatDate(user.last_login) : 'Never'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
