export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'editor' | 'viewer';
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  data: {
    user: User;
    sessionid: string;
  };
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface CreateUserData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: User['role'];
  is_active?: boolean;
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  full_name?: string;
  role?: User['role'];
  is_active?: boolean;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
}
