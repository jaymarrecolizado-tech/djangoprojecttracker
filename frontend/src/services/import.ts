import apiClient from './api';
import type { ApiResponse, ImportJob, ImportProgress, ImportError } from '@/types/api';

/**
 * Import/Export Service
 * 
 * Handles CSV import/export operations and file uploads.
 * Endpoints:
 * - POST /api/v1/import/imports/upload/ - Upload CSV file
 * - GET /api/v1/import/imports/{id}/progress/ - Get import progress
 * - GET /api/v1/import/imports/ - List all imports
 * - GET /api/v1/import/imports/{id}/ - Get import details
 * - GET /api/v1/export/ - Export data
 */

export interface ImportUploadResponse {
  import: ImportJob;
}

export interface ImportListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ImportJob[];
}

export interface ImportProgressResponse {
  import: ImportJob;
}

export interface ExportOptions {
  format: 'csv' | 'excel' | 'json';
  model: 'projects' | 'locations' | 'users';
  filters?: Record<string, string | number | boolean>;
}

export const importService = {
  /**
   * Upload a CSV file for import
   * @param file - CSV file to upload
   * @returns Import job information
   */
  async uploadCSV(file: File): Promise<ImportJob> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.getInstance().post<ApiResponse<ImportUploadResponse>>(
      'import/imports/upload/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data.import;
  },

  /**
   * Get import progress
   * @param importId - ID of the import job
   * @returns Current import status and progress
   */
  async getProgress(importId: number): Promise<ImportJob> {
    const response = await apiClient.get<ApiResponse<ImportProgressResponse>>(`import/imports/${importId}/progress/`);
    return response.data.import;
  },

  /**
   * Get list of all imports
   * @param page - Page number for pagination
   * @param pageSize - Items per page
   * @returns Paginated list of imports
   */
  async getImports(page = 1, pageSize = 20): Promise<ImportListResponse> {
    const response = await apiClient.getInstance().get<ImportListResponse>('import/imports/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Get import details by ID
   * @param importId - ID of the import job
   * @returns Detailed import information
   */
  async getImport(importId: number): Promise<ImportJob> {
    const response = await apiClient.getInstance().get<ApiResponse<{ import: ImportJob }>>(`import/imports/${importId}/`);
    return response.data.data.import;
  },

  /**
   * Cancel an ongoing import
   * @param importId - ID of the import job to cancel
   */
  async cancelImport(importId: number): Promise<void> {
    await apiClient.getInstance().post(`import/imports/${importId}/cancel/`);
  },

  /**
   * Delete an import record
   * @param importId - ID of the import job to delete
   */
  async deleteImport(importId: number): Promise<void> {
    await apiClient.getInstance().delete(`import/imports/${importId}/`);
  },

  /**
   * Retry a failed import
   * @param importId - ID of the failed import job
   * @returns New import job information
   */
  async retryImport(importId: number): Promise<ImportJob> {
    const response = await apiClient.getInstance().post<ApiResponse<ImportUploadResponse>>(
      `import/imports/${importId}/retry/`
    );
    return response.data.data.import;
  },

  /**
   * Export data to various formats
   * @param options - Export options
   * @returns Blob containing the exported file
   */
  async exportData(options: ExportOptions): Promise<Blob> {
    const response = await apiClient.getInstance().get('export/', {
      params: {
        format: options.format,
        model: options.model,
        ...options.filters,
      },
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Export projects to CSV
   * @param filters - Optional filters for the export
   * @returns Blob containing CSV file
   */
  async exportProjectsCSV(filters?: Record<string, string | number | boolean>): Promise<Blob> {
    return this.exportData({
      format: 'csv',
      model: 'projects',
      filters,
    });
  },

  /**
   * Export projects to Excel
   * @param filters - Optional filters for the export
   * @returns Blob containing Excel file
   */
  async exportProjectsExcel(filters?: Record<string, string | number | boolean>): Promise<Blob> {
    return this.exportData({
      format: 'excel',
      model: 'projects',
      filters,
    });
  },

  /**
   * Download export file with proper filename
   * @param blob - File blob
   * @param filename - Suggested filename
   */
  downloadFile(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  /**
   * Validate CSV file before upload
   * @param file - File to validate
   * @returns Validation result
   */
  validateCSVFile(file: File): { valid: boolean; error?: string } {
    // Check file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      return { valid: false, error: 'File must be a CSV file' };
    }

    // Check file size (max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB in bytes
    if (file.size > maxSize) {
      return { valid: false, error: 'File size exceeds 100MB limit' };
    }

    // Check if file is empty
    if (file.size === 0) {
      return { valid: false, error: 'File is empty' };
    }

    return { valid: true };
  },

  /**
   * Parse import errors for display
   * @param importJob - Import job with errors
   * @returns Formatted error messages
   */
  parseImportErrors(importJob: ImportJob): string[] {
    if (!importJob.errors || importJob.errors.length === 0) {
      return [];
    }

    return importJob.errors.map((error: ImportError) => 
      `Row ${error.row}: ${error.field} - ${error.message}`
    );
  },

  /**
   * Calculate import progress percentage
   * @param importJob - Import job
   * @returns Progress percentage (0-100)
   */
  calculateProgress(importJob: ImportJob): number {
    if (importJob.total_rows === 0) return 0;
    
    const processed = importJob.success_count + importJob.error_count;
    return Math.round((processed / importJob.total_rows) * 100);
  },
};

export default importService;
