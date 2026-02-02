import apiClient from './api';
import type { 
  ProjectSite, 
  ProjectSiteListItem,
  ProjectStatusHistory,
  CreateProjectData,
  UpdateProjectData,
  StatusChangeData,
  ProjectFilters,
  PaginatedResponse,
  ProjectType
} from '@/types';

export const projectsService = {
  async getProjects(filters?: ProjectFilters & { page?: number; page_size?: number }): Promise<PaginatedResponse<ProjectSiteListItem>> {
    const response = await apiClient.get<PaginatedResponse<ProjectSiteListItem>>('projects/', { params: filters });
    return response.data;
  },

  async getProject(id: number): Promise<ProjectSite> {
    const response = await apiClient.get<ProjectSite>(`projects/${id}/`);
    return response.data;
  },

  async createProject(data: CreateProjectData): Promise<ProjectSite> {
    const response = await apiClient.post<ProjectSite>('projects/', data);
    return response.data;
  },

  async updateProject(id: number, data: UpdateProjectData): Promise<ProjectSite> {
    const response = await apiClient.put<ProjectSite>(`projects/${id}/`, data);
    return response.data;
  },

  async deleteProject(id: number): Promise<void> {
    await apiClient.delete(`projects/${id}/`);
  },

  async getProjectHistory(id: number): Promise<ProjectStatusHistory[]> {
    const response = await apiClient.get<ProjectStatusHistory[]>(`projects/${id}/history/`);
    return response.data;
  },

  async changeStatus(id: number, data: StatusChangeData): Promise<void> {
    await apiClient.post(`projects/${id}/change-status/`, data);
  },
};

export const projectTypesService = {
  async getProjectTypes(): Promise<ProjectType[]> {
    const response = await apiClient.get<ProjectType[]>('project-types/');
    return response.data;
  },
};
