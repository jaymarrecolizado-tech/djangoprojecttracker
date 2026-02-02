import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '@/services/auth';
import { useAuthStore } from '@/stores/auth';
import type { LoginCredentials, User } from '@/types';

export function useAuth() {
  const queryClient = useQueryClient();
  const { setUser, setAuthenticated, setLoading, logout: storeLogout } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (response) => {
      setUser(response.data.user);
      setAuthenticated(true);
      queryClient.setQueryData(['currentUser'], response.data.user);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      storeLogout();
      queryClient.clear();
    },
  });

  const currentUserQuery = useQuery({
    queryKey: ['currentUser'],
    queryFn: async (): Promise<User | null> => {
      try {
        const user = await authService.getCurrentUser();
        setUser(user);
        setAuthenticated(true);
        return user;
      } catch {
        setUser(null);
        setAuthenticated(false);
        return null;
      } finally {
        setLoading(false);
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  return {
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    currentUser: currentUserQuery.data,
    isLoading: currentUserQuery.isLoading,
    loginError: loginMutation.error,
  };
}
