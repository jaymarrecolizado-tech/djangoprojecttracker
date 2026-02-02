import apiClient from './api';
import type { ApiResponse } from '@/types/api';

/**
 * Reports Service
 * 
 * Handles all API calls related to reports, statistics, and analytics.
 * Endpoints:
 * - GET /api/v1/reports/statistics/ - Overall project statistics
 * - GET /api/v1/reports/distribution/ - Project distribution by location
 * - GET /api/v1/reports/timeline/ - Project creation timeline
 */

export interface ProjectStatistics {
  total_projects: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
}

export interface ProjectDistribution {
  by_province: Record<string, number>;
}

export interface TimelineData {
  month: string;
  count: number;
}

export interface ProjectTimeline {
  timeline: TimelineData[];
}

export interface StatusDistribution {
  status: string;
  count: number;
  percentage: number;
  color: string;
}

export interface TypeDistribution {
  type: string;
  count: number;
  percentage: number;
}

export interface LocationDistribution {
  province: string;
  count: number;
  percentage: number;
}

export interface ComprehensiveReport {
  statistics: ProjectStatistics;
  distribution: ProjectDistribution;
  timeline: TimelineData[];
}

export const reportsService = {
  /**
   * Get overall project statistics
   * Returns total projects, counts by status, and counts by type
   */
  async getStatistics(): Promise<ProjectStatistics> {
    const response = await apiClient.get<ApiResponse<{ statistics: ProjectStatistics }>>('reports/statistics/');
    return response.data.statistics;
  },

  /**
   * Get project distribution by location
   * Returns project counts grouped by province
   */
  async getDistribution(): Promise<ProjectDistribution> {
    const response = await apiClient.get<ApiResponse<{ distribution: ProjectDistribution }>>('reports/distribution/');
    return response.data.distribution;
  },

  /**
   * Get project timeline data
   * Returns monthly project creation counts
   */
  async getTimeline(): Promise<TimelineData[]> {
    const response = await apiClient.get<ApiResponse<{ timeline: TimelineData[] }>>('reports/timeline/');
    return response.data.timeline;
  },

  /**
   * Get all reports in a single call
   * Combines statistics, distribution, and timeline
   */
  async getComprehensiveReport(): Promise<ComprehensiveReport> {
    const [statistics, distribution, timeline] = await Promise.all([
      this.getStatistics(),
      this.getDistribution(),
      this.getTimeline(),
    ]);

    return {
      statistics,
      distribution,
      timeline,
    };
  },

  /**
   * Get status distribution with calculated percentages
   */
  async getStatusDistribution(): Promise<StatusDistribution[]> {
    const statistics = await this.getStatistics();
    const total = statistics.total_projects;

    const statusColors: Record<string, string> = {
      pending: '#F59E0B',
      in_progress: '#3B82F6',
      done: '#10B981',
      cancelled: '#EF4444',
      on_hold: '#6B7280',
    };

    return Object.entries(statistics.by_status).map(([status, count]) => ({
      status,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
      color: statusColors[status] || '#9CA3AF',
    }));
  },

  /**
   * Get type distribution with calculated percentages
   */
  async getTypeDistribution(): Promise<TypeDistribution[]> {
    const statistics = await this.getStatistics();
    const total = statistics.total_projects;

    const typeEntries = Object.entries(statistics.by_type);
    const totalTyped = typeEntries.reduce((sum, [, count]) => sum + count, 0);

    return typeEntries.map(([type, count]) => ({
      type,
      count,
      percentage: totalTyped > 0 ? Math.round((count / totalTyped) * 100) : 0,
    }));
  },

  /**
   * Get location distribution with calculated percentages
   */
  async getLocationDistribution(): Promise<LocationDistribution[]> {
    const distribution = await this.getDistribution();
    
    const provinceEntries = Object.entries(distribution.by_province);
    const total = provinceEntries.reduce((sum, [, count]) => sum + count, 0);

    return provinceEntries
      .map(([province, count]) => ({
        province,
        count,
        percentage: total > 0 ? Math.round((count / total) * 100) : 0,
      }))
      .sort((a, b) => b.count - a.count);
  },

  /**
   * Export report data
   * @param format - Export format ('csv', 'excel', 'pdf')
   * @param reportType - Type of report to export
   */
  async exportReport(format: 'csv' | 'excel' | 'pdf', reportType: 'statistics' | 'distribution' | 'timeline'): Promise<Blob> {
    const response = await apiClient.getInstance().get(`reports/export/`, {
      params: { format, report_type: reportType },
      responseType: 'blob',
    });
    return response.data;
  },
};

export default reportsService;
