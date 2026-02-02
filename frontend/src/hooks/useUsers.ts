import { useQuery, useMutation, useQueryClient, useState } from '@tanstack/react-query';
import { usersService } from '@/services/users';
import type { User, CreateUserData, UpdateUserData } from '@/types';
import type { UserFilters, UserListResponse, UserStats } from '@/services/users';

const USERS_QUERY_KEY = 'users';
const USER_STATS_QUERY_KEY = 'user-stats';

export function useUsers(filters?: UserFilters & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: [USERS_QUERY_KEY, filters],
    queryFn: () => usersService.getUsers(filters),
    staleTime: 30 * 1000,
  });
}

export function useUser(id: number) {
  return useQuery({
    queryKey: [USERS_QUERY_KEY, id],
    queryFn: () => usersService.getUser(id),
    enabled: !!id,
  });
}

export function useUserStats() {
  return useQuery({
    queryKey: [USER_STATS_QUERY_KEY],
    queryFn: () => usersService.getUserStats(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSearchUsers(query: string) {
  return useQuery({
    queryKey: [USERS_QUERY_KEY, 'search', query],
    queryFn: () => usersService.searchUsers(query),
    enabled: query.length >= 2,
    staleTime: 30 * 1000,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserData) => usersService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [USER_STATS_QUERY_KEY] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateUserData }) =>
      usersService.updateUser(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

export function usePatchUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<UpdateUserData> }) =>
      usersService.patchUser(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersService.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [USER_STATS_QUERY_KEY] });
    },
  });
}

export function useActivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersService.activateUser(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

export function useDeactivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersService.deactivateUser(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

export function useChangeUserRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, role }: { id: number; role: User['role'] }) =>
      usersService.changeUserRole(id, role),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

export function useBulkDeleteUsers() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userIds: number[]) => usersService.bulkDeleteUsers(userIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [USER_STATS_QUERY_KEY] });
    },
  });
}

export function useBulkUpdateUserStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userIds, isActive }: { userIds: number[]; isActive: boolean }) =>
      usersService.bulkUpdateStatus(userIds, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_QUERY_KEY] });
    },
  });
}

/**
 * Hook for managing users with all CRUD operations
 */
export function useUsersManager() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<UserFilters>({});

  const {
    data: usersData,
    isLoading,
    error,
    refetch,
  } = useUsers({ ...filters, page, page_size: 10, search });

  const createUser = useCreateUser();
  const updateUser = useUpdateUser();
  const deleteUser = useDeleteUser();
  const activateUser = useActivateUser();
  const deactivateUser = useDeactivateUser();
  const changeUserRole = useChangeUserRole();
  const bulkDeleteUsers = useBulkDeleteUsers();

  const users = usersData?.results || [];
  const totalPages = usersData ? Math.ceil(usersData.count / 10) : 1;
  const totalCount = usersData?.count || 0;

  const handleCreateUser = async (data: CreateUserData) => {
    await createUser.mutateAsync(data);
  };

  const handleUpdateUser = async (id: number, data: UpdateUserData) => {
    await updateUser.mutateAsync({ id, data });
  };

  const handleDeleteUser = async (id: number) => {
    await deleteUser.mutateAsync(id);
  };

  const handleActivateUser = async (id: number) => {
    await activateUser.mutateAsync(id);
  };

  const handleDeactivateUser = async (id: number) => {
    await deactivateUser.mutateAsync(id);
  };

  const handleChangeUserRole = async (id: number, role: User['role']) => {
    await changeUserRole.mutateAsync({ id, role });
  };

  const handleBulkDelete = async (userIds: number[]) => {
    await bulkDeleteUsers.mutateAsync(userIds);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleSearch = (searchQuery: string) => {
    setSearch(searchQuery);
    setPage(1);
  };

  const handleFilterChange = (newFilters: UserFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  return {
    // Data
    users,
    totalCount,
    totalPages,
    currentPage: page,
    
    // Loading states
    isLoading,
    error,
    isCreating: createUser.isPending,
    isUpdating: updateUser.isPending,
    isDeleting: deleteUser.isPending,
    isActivating: activateUser.isPending,
    isDeactivating: deactivateUser.isPending,
    
    // Actions
    refetch,
    setPage: handlePageChange,
    setSearch: handleSearch,
    setFilters: handleFilterChange,
    createUser: handleCreateUser,
    updateUser: handleUpdateUser,
    deleteUser: handleDeleteUser,
    activateUser: handleActivateUser,
    deactivateUser: handleDeactivateUser,
    changeUserRole: handleChangeUserRole,
    bulkDelete: handleBulkDelete,
    
    // Error handling
    createError: createUser.error,
    updateError: updateUser.error,
    deleteError: deleteUser.error,
  };
}
