// API Response types

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

export interface ValidationError {
  field: string;
  errors: string[];
}

export interface ImportJob {
  id: number;
  file_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_rows: number;
  success_count: number;
  error_count: number;
  errors: ImportError[];
  uploaded_at: string;
  started_at: string | null;
  completed_at: string | null;
  uploaded_by: number;
}

export interface ImportError {
  row: number;
  field: string;
  message: string;
}

export interface ImportProgress {
  id: number;
  status: ImportJob['status'];
  progress: number;
  total_rows: number;
  processed_rows: number;
  success_count: number;
  error_count: number;
}

export interface ReportStatistics {
  total_projects: number;
  status_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
  monthly_trend: Array<{
    month: string;
    count: number;
  }>;
  location_distribution: Array<{
    province: string;
    count: number;
  }>;
}

export interface Notification {
  id: number;
  notification_type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  data: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: number;
  action: string;
  model_name: string;
  object_id: number;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  ip_address: string;
  created_at: string;
  user: {
    id: number;
    username: string;
    full_name: string;
  };
}

export interface WebSocketMessage {
  type: 'notification' | 'import_progress' | 'project_update';
  data: unknown;
  timestamp: string;
}
