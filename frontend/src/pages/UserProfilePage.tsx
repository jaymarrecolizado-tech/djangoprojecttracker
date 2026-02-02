import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { User, Lock, Save } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { authService } from '@/services/auth'
import { changePasswordSchema, type ChangePasswordFormData } from '@/lib/validators'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'
import { useState } from 'react'

export function UserProfilePage() {
  const { currentUser, isLoading: userLoading } = useAuth()
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  const passwordForm = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      old_password: '',
      new_password: '',
      confirm_password: '',
    },
  })

  const handlePasswordChange = async (data: ChangePasswordFormData) => {
    try {
      await authService.changePassword({
        old_password: data.old_password,
        new_password: data.new_password,
      })
      toast.success('Password changed successfully')
      setIsChangingPassword(false)
      passwordForm.reset()
    } catch {
      toast.error('Failed to change password')
    }
  }

  if (userLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h2 className="text-2xl font-bold">Not authenticated</h2>
      </div>
    )
  }

  const initials = currentUser.full_name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">
          Manage your account settings
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Profile Information
            </CardTitle>
            <CardDescription>
              Your account details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <Avatar className="h-20 w-20">
                <AvatarFallback className="text-2xl">{initials}</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-xl font-semibold">{currentUser.full_name}</p>
                <p className="text-muted-foreground">{currentUser.email}</p>
              </div>
            </div>
            <div className="grid gap-4 pt-4">
              <div>
                <Label>Username</Label>
                <p className="text-sm">{currentUser.username}</p>
              </div>
              <div>
                <Label>Role</Label>
                <p className="text-sm capitalize">{currentUser.role}</p>
              </div>
              <div>
                <Label>Member Since</Label>
                <p className="text-sm">
                  {new Date(currentUser.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Change Password */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5" />
              Change Password
            </CardTitle>
            <CardDescription>
              Update your password
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isChangingPassword ? (
              <form onSubmit={passwordForm.handleSubmit(handlePasswordChange)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="old_password">Current Password</Label>
                  <Input
                    id="old_password"
                    type="password"
                    {...passwordForm.register('old_password')}
                  />
                  {passwordForm.formState.errors.old_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.old_password.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password</Label>
                  <Input
                    id="new_password"
                    type="password"
                    {...passwordForm.register('new_password')}
                  />
                  {passwordForm.formState.errors.new_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.new_password.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    {...passwordForm.register('confirm_password')}
                  />
                  {passwordForm.formState.errors.confirm_password && (
                    <p className="text-sm text-destructive">
                      {passwordForm.formState.errors.confirm_password.message}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={passwordForm.formState.isSubmitting}>
                    <Save className="mr-2 h-4 w-4" />
                    {passwordForm.formState.isSubmitting ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsChangingPassword(false)
                      passwordForm.reset()
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            ) : (
              <Button onClick={() => setIsChangingPassword(true)} variant="outline">
                <Lock className="mr-2 h-4 w-4" />
                Change Password
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
