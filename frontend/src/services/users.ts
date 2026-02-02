import apiClient from './api';
import type {
  User,
  CreateUserData,
  UpdateUserData,
  PaginatedResponse
} from '@/types/auth';
import type { ApiResponse } from '@/types/api';

/**
 * Users Management Service
 * 
 * Handles user management operations (CRUD) for administrators.
 * Endpoints:
 * - GET /api/v1/auth/users/ - List all users
 * - GET /api/v1/auth/users/{id}/ - Get user details
 * - POST /api/v1/auth/users/ - Create new user
 * - PUT /api/v1/auth/users/{id}/ - Update user
 * - DELETE /api/v1/auth/users/{id}/ - Delete user
 */

export interface UserFilters {
  search?: string;
  role?: string;
  is_active?: boolean;
  ordering?: string;
}

export interface UserListParams extends UserFilters {
  page?: number;
  page_size?: number;
}

export interface UserListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];
}

export interface UserStats {
  total_users: number;
  active_users: number;
  users_by_role: Record<string, number>;
  recent_users: User[];
}

export const usersService = {
  /**
   * Get list of all users with pagination and filtering
   * @param params - Filter and pagination parameters
   * @returns Paginated list of users
   */
  async getUsers(params?: UserListParams): Promise<UserListResponse> {
    const response = await apiClient.getInstance().get<ApiResponse<UserListResponse>>('auth/users/', { 
      params 
    });
    return response.data.data;
  },

  /**
   * Get a single user by ID
   * @param userId - User ID
   * @returns User details
   */
  async getUser(userId: number): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>(`auth/users/${userId}/`);
    return response.data;
  },

  /**
   * Create a new user
   * @param data - User creation data
   * @returns Created user
   */
  async createUser(data: CreateUserData): Promise<User> {
    const response = await apiClient.getInstance().post<ApiResponse<User>>('auth/users/', data);
    return response.data.data;
  },

  /**
   * Update an existing user
   * @param userId - User ID to update
   * @param data - User update data
   * @returns Updated user
   */
  async updateUser(userId: number, data: UpdateUserData): Promise<User> {
    const response = await apiClient.getInstance().put<ApiResponse<User>>(`auth/users/${userId}/`, data);
    return response.data.data;
  },

  /**
   * Partially update a user (PATCH)
   * @param userId - User ID to update
   * @param data - Partial user update data
   * @returns Updated user
   */
  async patchUser(userId: number, data: Partial<UpdateUserData>): Promise<User> {
    const response = await apiClient.getInstance().patch<ApiResponse<User>>(`auth/users/${userId}/`, data);
    return response.data.data;
  },

  /**
   * Delete a user
   * @param userId - User ID to delete
   */
  async deleteUser(userId: number): Promise<void> {
    await apiClient.getInstance().delete(`auth/users/${userId}/`);
  },

  /**
   * Activate a user account
   * @param userId - User ID to activate
   * @returns Updated user
   */
  async activateUser(userId: number): Promise<User> {
    return this.patchUser(userId, { is_active: true });
  },

  /**
   * Deactivate a user account
   * @param userId - User ID to deactivate
   * @returns Updated user
   */
  async deactivateUser(userId: number): Promise<User> {
    return this.patchUser(userId, { is_active: false });
  },

  /**
   * Change user role
   * @param userId - User ID
   * @param role - New role (admin, manager, editor, viewer)
   * @returns Updated user
   */
  async changeUserRole(userId: number, role: User['role']): Promise<User> {
    return this.patchUser(userId, { role });
  },

  /**
   * Reset user password (admin action)
   * @param userId - User ID
   * @param newPassword - New password
   */
  async resetPassword(userId: number, newPassword: string): Promise<void> {
    await apiClient.getInstance().post(`auth/users/${userId}/reset-password/`, {
      new_password: newPassword,
    });
  },

  /**
   * Get user statistics
   * @returns User statistics
   */
  async getUserStats(): Promise<UserStats> {
    const response = await apiClient.get<ApiResponse<UserStats>>('auth/users/stats/');
    return response.data;
  },

  /**
   * Search users by name, email, or username
   * @param query - Search query
   * @param limit - Maximum results to return
   * @returns List of matching users
   */
  async searchUsers(query: string, limit = 20): Promise<User[]> {
    const response = await apiClient.get<ApiResponse<UserListResponse>>('auth/users/', {
      params: { search: query, page_size: limit },
    });
    return response.data.results;
  },

  /**
   * Get users by role
   * @param role - Role to filter by
   * @returns List of users with the specified role
   */
  async getUsersByRole(role: User['role']): Promise<User[]> {
    const response = await this.getUsers({ role, page_size: 1000 });
    return response.results;
  },

  /**
   * Bulk delete users
   * @param userIds - Array of user IDs to delete
   */
  async bulkDeleteUsers(userIds: number[]): Promise<void> {
    await apiClient.getInstance().post('auth/users/bulk-delete/', {
      user_ids: userIds,
    });
  },

  /**
   * Bulk update user status
   * @param userIds - Array of user IDs
   * @param isActive - New active status
   */
  async bulkUpdateStatus(userIds: number[], isActive: boolean): Promise<void> {
    await apiClient.getInstance().post('auth/users/bulk-update/', {
      user_ids: userIds,
      is_active: isActive,
    });
  },

  /**
   * Get current user's profile
   * Note: This is available in auth service, duplicated here for convenience
   * @returns Current user details
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>('auth/me/');
    return response.data;
  },

  /**
   * Update current user's profile
   * @param data - Profile update data
   * @returns Updated user
   */
  async updateProfile(data: Partial<UpdateUserData>): Promise<User> {
    const response = await apiClient.getInstance().patch<ApiResponse<User>>('auth/me/', data);
    return response.data.data;
  },
};

export default usersService;
