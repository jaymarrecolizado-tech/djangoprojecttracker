import apiClient from './api';
import type { 
  User, 
  LoginCredentials, 
  LoginResponse,
  CreateUserData,
  UpdateUserData,
  ChangePasswordData,
  PaginatedResponse 
} from '@/types';

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('auth/login/', credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('auth/logout/');
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('auth/me/');
    return response.data;
  },

  async changePassword(data: ChangePasswordData): Promise<void> {
    await apiClient.post('auth/change-password/', data);
  },
};

export const usersService = {
  async getUsers(params?: { page?: number; page_size?: number; search?: string }): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<PaginatedResponse<User>>('users/', { params });
    return response.data;
  },

  async getUser(id: number): Promise<User> {
    const response = await apiClient.get<User>(`users/${id}/`);
    return response.data;
  },

  async createUser(data: CreateUserData): Promise<User> {
    const response = await apiClient.post<User>('users/', data);
    return response.data;
  },

  async updateUser(id: number, data: UpdateUserData): Promise<User> {
    const response = await apiClient.put<User>(`users/${id}/`, data);
    return response.data;
  },

  async deleteUser(id: number): Promise<void> {
    await apiClient.delete(`users/${id}/`);
  },
};
