import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportsService } from '@/services/reports';
import { importService } from '@/services/import';
import type { 
  ProjectStatistics, 
  ProjectDistribution, 
  TimelineData,
  ComprehensiveReport,
  StatusDistribution,
  TypeDistribution,
  LocationDistribution,
} from '@/services/reports';

export interface DateRange {
  startDate?: string;
  endDate?: string;
}

export interface ExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  reportType: 'statistics' | 'distribution' | 'timeline';
  dateRange?: DateRange;
}

const REPORTS_QUERY_KEY = 'reports';

export function useStatistics(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'statistics', dateRange],
    queryFn: () => reportsService.getStatistics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDistribution(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'distribution', dateRange],
    queryFn: () => reportsService.getDistribution(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useTimeline(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'timeline', dateRange],
    queryFn: () => reportsService.getTimeline(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useComprehensiveReport(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'comprehensive', dateRange],
    queryFn: () => reportsService.getComprehensiveReport(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useStatusDistribution(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'statusDistribution', dateRange],
    queryFn: () => reportsService.getStatusDistribution(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useTypeDistribution(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'typeDistribution', dateRange],
    queryFn: () => reportsService.getTypeDistribution(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useLocationDistribution(dateRange?: DateRange) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'locationDistribution', dateRange],
    queryFn: () => reportsService.getLocationDistribution(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useExportReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (options: ExportOptions) => {
      const blob = await reportsService.exportReport(options.format, options.reportType);
      
      // Generate filename
      const timestamp = new Date().toISOString().split('T')[0];
      const extension = options.format === 'excel' ? 'xlsx' : options.format;
      const filename = `report_${options.reportType}_${timestamp}.${extension}`;
      
      // Download the file
      importService.downloadFile(blob, filename);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REPORTS_QUERY_KEY] });
    },
  });
}

/**
 * Hook for managing all reports data with loading states
 */
export function useReports(dateRange?: DateRange) {
  const {
    data: statistics,
    isLoading: isStatisticsLoading,
    error: statisticsError,
  } = useStatistics(dateRange);

  const {
    data: distribution,
    isLoading: isDistributionLoading,
    error: distributionError,
  } = useDistribution(dateRange);

  const {
    data: timeline,
    isLoading: isTimelineLoading,
    error: timelineError,
  } = useTimeline(dateRange);

  const {
    data: statusDistribution,
    isLoading: isStatusDistributionLoading,
  } = useStatusDistribution(dateRange);

  const {
    data: typeDistribution,
    isLoading: isTypeDistributionLoading,
  } = useTypeDistribution(dateRange);

  const {
    data: locationDistribution,
    isLoading: isLocationDistributionLoading,
  } = useLocationDistribution(dateRange);

  const exportReport = useExportReport();

  const isLoading = 
    isStatisticsLoading || 
    isDistributionLoading || 
    isTimelineLoading ||
    isStatusDistributionLoading ||
    isTypeDistributionLoading ||
    isLocationDistributionLoading;

  const error = statisticsError || distributionError || timelineError;

  return {
    statistics,
    distribution,
    timeline,
    statusDistribution,
    typeDistribution,
    locationDistribution,
    isLoading,
    error,
    isExporting: exportReport.isPending,
    exportReport: exportReport.mutateAsync,
  };
}
